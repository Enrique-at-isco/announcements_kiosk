import json
import time
import threading
import os
import http.server
import socketserver
import shutil
from pynput import keyboard as pynput_keyboard
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ====== CONFIG =======
CONFIG_FILE = "config.json"
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
AUTO_CLICK_ON_BOOT = True
EXIT_HOTKEY = "esc"
LOCAL_SERVER_PORT = 8080
LOCAL_DIRECTORY = "/home/annkiosk/announcements_kiosk/html"
LOG_FILE = "/home/annkiosk/announcements_kiosk/kiosk_log.txt"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB

CHROMIUM_PROFILE_DIR = "/home/annkiosk/.config/chromium"
LOCK_FILE = os.path.join(CHROMIUM_PROFILE_DIR, "SingletonLock")
# =====================

class KioskController:
    def __init__(self):
        self.running = True
        self.driver = None
        self.httpd = None
        self.last_config_check = time.time()

        # Setup logging
        self.log_file = open(LOG_FILE, "a")
        self.log("Kiosk Controller initialized.")

        # Initial config load
        self.load_config()

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.log_file.write(log_message + "\n")
        self.log_file.flush()

        # Log rotation
        if os.path.getsize(LOG_FILE) > LOG_MAX_SIZE:
            self.log_file.close()
            backup_log = LOG_FILE + ".bak"
            shutil.move(LOG_FILE, backup_log)
            self.log_file = open(LOG_FILE, "a")
            self.log("Log rotated.")

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            self.urls = config.get("urls", [])
            self.cycle_delay = config.get("cycle_delay", 45)
            self.refresh_interval = config.get("refresh_interval", 120)
            self.log(f"Config loaded: {len(self.urls)} URLs, cycle_delay={self.cycle_delay}s, refresh_interval={self.refresh_interval}s")
        except Exception as e:
            self.log(f"Error loading config: {e}")

    def check_config_reload(self):
        # Reload config every 60 seconds
        if time.time() - self.last_config_check > 60:
            self.load_config()
            self.last_config_check = time.time()

    def clean_chromium_profile(self):
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            self.log("Removed Chromium profile lock file.")

    def start_local_server(self):
        os.chdir(LOCAL_DIRECTORY)
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("0.0.0.0", LOCAL_SERVER_PORT), handler)

        self.log(f"Serving local files at http://0.0.0.0:{LOCAL_SERVER_PORT}/")
        server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        server_thread.start()

    def start_browser(self):
        self.clean_chromium_profile()

        # Wait for X display to be ready
        for _ in range(30):
            if os.environ.get('DISPLAY') == ':0':
                break
            time.sleep(0.5)

        time.sleep(5)

        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        
        chrome_options.add_argument("--user-data-dir=" + CHROMIUM_PROFILE_DIR)
        chrome_options.add_argument("--profile-directory=Default")

        # Kiosk mode and UI cleanup
        chrome_options.add_argument("--kiosk")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")

        # Sandbox and security
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--allow-file-access-from-files")
        chrome_options.add_argument("--disable-web-security")

        # Performance and GPU settings
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--use-gl=swiftshader")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-smooth-scrolling")
        chrome_options.add_argument("--disable-low-res-tiling")
        chrome_options.add_argument("--enable-low-end-device-mode")
        chrome_options.add_argument("--disable-composited-antialiasing")

        # Features
        chrome_options.add_argument("--enable-accelerated-video-decode")
        chrome_options.add_argument("--enable-gpu-rasterization")
        chrome_options.add_argument("--enable-oop-rasterization")
        chrome_options.add_argument("--ignore-gpu-blocklist")
        chrome_options.add_argument("--enable-features=OverlayScrollbar")

        # Fast startup
        chrome_options.add_argument("--fast")
        chrome_options.add_argument("--fast-start")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--noerrdialogs")

        # Remote debugging
        chrome_options.add_argument("--remote-debugging-port=9222")

        # ✅ X11 specific: remove Wayland, ensure X11
        chrome_options.add_argument("--ozone-platform=x11")

        # ✅ Debugging and logging
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")


        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        for url in self.urls:
            self.driver.execute_script(f"window.open('{url}', '_blank');")

        # Close default tab
        if len(self.driver.window_handles) > 0:
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()

        self.log("Browser started and tabs loaded.")

    def auto_click_sign_in(self):
        try:
            self.driver.switch_to.frame(0)
            for attempt in range(5):
                try:
                    sign_in_span = self.driver.find_element(By.CSS_SELECTOR, "span[data-bind='text:actionText']")
                    sign_in_button = sign_in_span.find_element(By.XPATH, "./ancestor::button")
                    self.driver.execute_script("arguments[0].click();", sign_in_button)
                    self.log("Auto-clicked sign-in button.")
                    break
                except Exception:
                    time.sleep(1)
        except Exception as e:
            self.log(f"Error in auto_click_sign_in: {e}")
        finally:
            self.driver.switch_to.default_content()

    def passive_sign_in_monitor(self):
        self.log("Starting passive sign-in monitor...")
        while self.running:
            for handle in self.driver.window_handles:
                try:
                    self.driver.switch_to.window(handle)
                    self.driver.switch_to.frame(0)
                    sign_in_elements = self.driver.find_elements(By.CSS_SELECTOR, "span[data-bind='text:actionText']")
                    if sign_in_elements:
                        sign_in_span = sign_in_elements[0]
                        sign_in_button = sign_in_span.find_element(By.XPATH, "./ancestor::button")
                        self.driver.execute_script("arguments[0].click();", sign_in_button)
                        self.log(f"Passive monitor: Auto-clicked sign-in button on tab: {self.driver.current_url}")
                except Exception:
                    pass
                finally:
                    try:
                        self.driver.switch_to.default_content()
                    except Exception:
                        pass
            time.sleep(5)

    def cycle_tabs(self):
        first_cycle = True
        while self.running:
            self.check_config_reload()
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                self.log(f"Switched to tab: {self.driver.current_url}")
                if AUTO_CLICK_ON_BOOT and first_cycle:
                    self.auto_click_sign_in()
                time.sleep(self.cycle_delay)
            first_cycle = False

    def refresh_tabs(self):
        while self.running:
            time.sleep(self.refresh_interval)
            self.log("Refreshing all tab iframes...")
            for handle in self.driver.window_handles:
                try:
                    self.driver.switch_to.window(handle)
                    self.driver.execute_script("""
                        let iframe = document.querySelector('iframe');
                        if (iframe) iframe.src = iframe.src;
                    """)
                    self.log(f"Refreshed iframe in tab: {self.driver.current_url}")
                except Exception as e:
                    self.log(f"Error refreshing iframe in tab: {e}")

    def start_hotkey_listener(self):
        def on_press(key):
            try:
                if key == pynput_keyboard.Key.esc:
                    self.log("Exit hotkey pressed!")
                    self.exit_kiosk()
            except AttributeError:
                pass

        listener = pynput_keyboard.Listener(on_press=on_press)
        listener.start()

    def exit_kiosk(self):
        self.log("Exiting kiosk mode...")
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.log(f"Error quitting driver: {e}")
        if self.httpd:
            self.httpd.shutdown()
            self.log("Local server stopped.")

        os.system("pkill chromium-browser")
        self.log("Chromium forcibly closed.")
        self.log("Kiosk shutdown complete.")
        self.log_file.close()
        exit(0)

    def run(self):
        self.log("Starting kiosk controller...")
        self.start_local_server()
        self.start_browser()

        threading.Thread(target=self.cycle_tabs).start()
        threading.Thread(target=self.refresh_tabs).start()
        threading.Thread(target=self.passive_sign_in_monitor).start()

        self.start_hotkey_listener()


if __name__ == "__main__":
    kiosk = KioskController()
    kiosk.run()
