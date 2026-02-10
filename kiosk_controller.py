#!/usr/bin/env python3
"""
Kiosk Controller - Main Display System
Cycles through configured URLs in Chromium browser for Raspberry Pi kiosk display
"""

import time
import json
import threading
import signal
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configuration paths
CONFIG_FILE = Path('/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json')
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
CHROMIUM_BINARY = "/usr/bin/chromium-browser"

# For development/testing in codespace
if not CONFIG_FILE.exists():
    CONFIG_FILE = Path('./config.json')


class KioskController:
    """
    Main controller for the kiosk display system.
    Manages browser lifecycle, tab cycling, and configuration reloading.
    """
    
    def __init__(self):
        self.driver = None
        self.urls = []
        self.current_tab = 0
        self.cycle_delay = 10  # default delay in seconds
        self.stop_event = threading.Event()
        self.config_last_modified = None
        
        # Load initial configuration
        self.load_config()
        
        # Handle termination signals for clean shutdown
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}", flush=True)
        
    def _handle_signal(self, signum, frame):
        """Handle termination signals for clean shutdown"""
        self.log(f"[INFO] Received signal {signum}, shutting down gracefully...")
        self.stop_event.set()
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if not CONFIG_FILE.exists():
                raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
            
            # Check if config has been modified
            current_mtime = CONFIG_FILE.stat().st_mtime
            if self.config_last_modified and current_mtime == self.config_last_modified:
                return  # No changes
                
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # Validate URLs
            urls = config.get('urls', [])
            if not urls:
                raise ValueError("No URLs configured in config.json")
            
            if not all(isinstance(url, str) and url.strip() for url in urls):
                raise ValueError("All URLs must be non-empty strings")
            
            self.urls = urls
            self.cycle_delay = int(config.get('cycle_delay', 10))
            
            if self.cycle_delay <= 0:
                raise ValueError("cycle_delay must be a positive integer")
            
            self.config_last_modified = current_mtime
            self.log(f"[INFO] Loaded {len(self.urls)} URLs with cycle delay of {self.cycle_delay}s")
            
        except FileNotFoundError as e:
            self.log(f"[ERROR] Config file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            self.log(f"[ERROR] Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            self.log(f"[ERROR] Error loading config: {e}")
            raise
            
    def check_config_reload(self):
        """Check if config has changed and reload if needed"""
        try:
            if CONFIG_FILE.exists():
                current_mtime = CONFIG_FILE.stat().st_mtime
                if current_mtime != self.config_last_modified:
                    self.log("[INFO] Config file changed, reloading...")
                    old_urls = self.urls[:]
                    self.load_config()
                    
                    # If URLs changed significantly, restart browser
                    if old_urls != self.urls:
                        self.log("[INFO] URLs changed, browser restart required")
                        return True
        except Exception as e:
            self.log(f"[WARN] Error checking config reload: {e}")
        
        return False
        
    def create_driver(self):
        """Create and configure the Chrome WebDriver"""
        self.log("[INFO] Creating Chrome driver...")
        
        chrome_options = Options()
        
        # Set Chromium binary location
        chrome_options.binary_location = CHROMIUM_BINARY
        
        # Kiosk mode settings
        chrome_options.add_argument("--kiosk")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--noerrdialogs")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-session-crashed-bubble")
        chrome_options.add_argument("--disable-restore-session-state")
        
        # Allow loading local file:// URLs
        chrome_options.add_argument("--allow-file-access-from-files")
        chrome_options.add_argument("--allow-file-access")
        
        # Disable distracting features
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-pinch")
        chrome_options.add_argument("--overscroll-history-navigation=0")
        chrome_options.add_argument("--disable-gesture-typing")
        
        # Performance optimizations for Raspberry Pi
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        
        # Logging (helpful for debugging)
        chrome_options.add_argument("--enable-logging=stderr")
        chrome_options.add_argument("--v=1")
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Create driver
        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
        self.log("[INFO] Chrome driver created successfully")
        
    def open_tabs(self):
        """Open all configured URLs in separate tabs"""
        if not self.urls:
            self.log("[ERROR] No URLs to open")
            return
            
        self.log(f"[INFO] Opening {len(self.urls)} tabs...")
        
        # Open first URL in current tab
        self.driver.get(self.urls[0])
        self.log(f"[INFO] Tab 1: {self.urls[0]}")
        
        # Open remaining URLs in new tabs
        for i, url in enumerate(self.urls[1:], start=2):
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            self.log(f"[INFO] Tab {i}: {url}")
        
        # Give tabs time to load
        time.sleep(5)
        
        # Verify all tabs opened
        handles = self.driver.window_handles
        self.log(f"[INFO] Successfully opened {len(handles)} browser tabs")
        
        # Switch back to first tab
        self.driver.switch_to.window(handles[0])
        self.current_tab = 0
        
    def cycle_tabs(self):
        """Continuously cycle through tabs, switching at configured intervals"""
        self.log("[INFO] Starting tab cycling...")
        
        while not self.stop_event.is_set():
            try:
                handles = self.driver.window_handles
                
                if not handles:
                    self.log("[ERROR] No browser tabs available")
                    break
                
                # Move to next tab
                self.current_tab = (self.current_tab + 1) % len(handles)
                self.driver.switch_to.window(handles[self.current_tab])
                
                # Log current tab (useful for monitoring)
                try:
                    current_url = self.driver.current_url
                    self.log(f"[INFO] Tab {self.current_tab + 1}/{len(handles)}: {current_url[:80]}")
                except:
                    self.log(f"[INFO] Switched to tab {self.current_tab + 1}/{len(handles)}")
                
                # Refresh current tab to get latest data
                try:
                    self.driver.refresh()
                except Exception as e:
                    self.log(f"[WARN] Failed to refresh tab: {e}")
                
                # Check for config changes every cycle
                if self.check_config_reload():
                    self.log("[INFO] Restarting browser due to config change...")
                    self.stop_event.set()
                    break
                
                # Wait for configured delay
                self.stop_event.wait(self.cycle_delay)
                
            except Exception as e:
                self.log(f"[ERROR] Error during tab cycling: {e}")
                time.sleep(5)  # Brief pause before retrying
                
    def start_browser(self):
        """Start the browser with retry logic"""
        retry_count = 0
        max_retries = 3
        
        while not self.stop_event.is_set() and retry_count < max_retries:
            try:
                self.create_driver()
                self.open_tabs()
                return True
            except Exception as e:
                retry_count += 1
                self.log(f"[ERROR] Failed to start browser (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    self.log("[INFO] Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    self.log("[ERROR] Max retries reached, giving up")
                    return False
                    
        return False
        
    def cleanup(self):
        """Clean up resources"""
        self.log("[INFO] Cleaning up resources...")
        
        if self.driver:
            try:
                self.driver.quit()
                self.log("[INFO] Browser closed successfully")
            except Exception as e:
                self.log(f"[WARN] Error closing browser: {e}")
                
    def run(self):
        """Main run loop"""
        self.log("=" * 60)
        self.log("[INFO] Kiosk Controller Starting")
        self.log(f"[INFO] Config file: {CONFIG_FILE}")
        self.log("=" * 60)
        
        try:
            # Start browser
            if not self.start_browser():
                self.log("[ERROR] Failed to start browser, exiting")
                return
            
            # Start tab cycling in background thread
            cycle_thread = threading.Thread(target=self.cycle_tabs, daemon=True)
            cycle_thread.start()
            
            # Main loop - just wait for stop signal
            while not self.stop_event.is_set():
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("[INFO] Keyboard interrupt received")
        except Exception as e:
            self.log(f"[ERROR] Unexpected error in main loop: {e}")
        finally:
            self.cleanup()
            self.log("[INFO] Kiosk Controller stopped")
            self.log("=" * 60)


def main():
    """Entry point"""
    kiosk = KioskController()
    kiosk.run()


if __name__ == "__main__":
    main()
