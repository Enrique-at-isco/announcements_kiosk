import time
import json
import threading
import signal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

CONFIG_FILE = '/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json'
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
CHROMIUM_BINARY   = "/usr/bin/chromium-browser"

class KioskController:
    def __init__(self):
        self.driver = None
        self.urls = []
        self.current_tab = 0
        self.cycle_delay = 10  # default, can be changed via config
        self.stop_event = threading.Event()
        self.load_config()

        # Handle termination signals so the kiosk can exit cleanly without pynput
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    def _handle_signal(self, signum, frame):
        """Handle termination signals by setting the stop event."""
        self.log(f"[INFO] Received signal {signum}, stopping kiosk...")
        self.stop_event.set()

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

            urls = config.get('urls', [])
            if not urls or not all(isinstance(url, str) and url.strip() for url in urls):
                raise ValueError("URLs in config must be a non-empty list of non-empty strings.")

            self.urls = urls
            self.cycle_delay = int(config.get('cycle_delay', 10))
            if self.cycle_delay <= 0:
                raise ValueError("cycle_delay must be a positive integer.")

            self.log(f"[INFO] Loaded {len(self.urls)} URLs with a cycle delay of {self.cycle_delay} seconds.")
        except FileNotFoundError:
            self.log(f"[ERROR] Config file not found: {CONFIG_FILE}")
            raise
        except json.JSONDecodeError as e:
            self.log(f"[ERROR] Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            self.log(f"[ERROR] Error loading config: {e}")
            raise

    def create_driver(self):
        self.log("[INFO] Creating Chrome driver (Chromium)...")

        chrome_options = Options()

        # Explicitly tell Selenium which Chromium to launch
        chrome_options.binary_location = CHROMIUM_BINARY

        # Kiosk / UI behaviour
        chrome_options.add_argument("--kiosk")
        chrome_options.add_argument("--noerrdialogs")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-restore-session-state")
        chrome_options.add_argument("--disable-session-crashed-bubble")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-pinch")
        chrome_options.add_argument("--overscroll-history-navigation=0")
        chrome_options.add_argument("--disable-gesture-typing")

        # Important for Pi / systemd / limited RAM
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Extra logging from Chromium itself so we can see why it dies if it does
        chrome_options.add_argument("--enable-logging=stderr")
        chrome_options.add_argument("--v=1")

        # Selenium-related tweaks
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)


    def open_initial_tabs(self):
        if not self.urls:
            self.log("[ERROR] No URLs configured to open.")
            return

        self.driver.get(self.urls[0])
        self.log(f"[INFO] Opened initial URL in first tab: {self.urls[0]}")

        for url in self.urls[1:]:
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            self.log(f"[INFO] Opened new tab with URL: {url}")

        time.sleep(5)

        handles = self.driver.window_handles
        self.log(f"[INFO] There are {len(handles)} browser tabs open.")

        for index, handle in enumerate(handles):
            self.driver.switch_to.window(handle)
            self.log(f"[INFO] Switched to tab {index + 1}/{len(handles)}.")
            time.sleep(3)

        self.driver.switch_to.window(handles[0])
        self.current_tab = 0
        self.log(f"[INFO] Reset focus to the first tab.")

    def click_signin_buttons(self):
        try:
            signin_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Sign in')]")
            if not signin_buttons:
                signin_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Sign in')]")

            if signin_buttons:
                self.log(f"[INFO] Found {len(signin_buttons)} 'Sign in' element(s). Clicking the first one.")
                signin_buttons[0].click()
            else:
                self.log("[INFO] No 'Sign in' elements found on this page.")
        except Exception as e:
            self.log(f"[ERROR] Error while trying to click 'Sign in' button: {e}")

    def cycle_tabs(self):
        if not self.driver or not self.urls:
            self.log("[ERROR] Cannot cycle tabs; driver not initialized or URLs not loaded.")
            return

        while not self.stop_event.is_set():
            try:
                handles = self.driver.window_handles
                if not handles:
                    self.log("[ERROR] No browser tabs available to cycle.")
                    break

                self.current_tab = (self.current_tab + 1) % len(handles)
                self.driver.switch_to.window(handles[self.current_tab])

                current_url = self.driver.current_url
                self.log(f"[INFO] Switched to tab {self.current_tab + 1}/{len(handles)}: {current_url}")

                if "https://accounts.google.com" in current_url:
                    self.log("[INFO] Detected Google login page. Attempting to click 'Sign in'.")
                    time.sleep(3)
                    self.click_signin_buttons()

                self.stop_event.wait(self.cycle_delay)
            except Exception as e:
                self.log(f"[ERROR] Error during tab cycling: {e}")

    def start_browser(self):
        while not self.stop_event.is_set():
            try:
                self.create_driver()
                self.open_initial_tabs()
                break
            except Exception as e:
                self.log(f"[ERROR] Failed to start browser: {e}. Retrying in 10 seconds...")
                time.sleep(10)

    def run(self):
        self.log("[INFO] Starting browser with Selenium...")
        self.start_browser()

        threading.Thread(target=self.cycle_tabs, daemon=True).start()

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        finally:
            if self.driver:
                self.driver.quit()
            self.log("[INFO] Kiosk Controller exited.")


if __name__ == "__main__":
    kiosk = KioskController()
    kiosk.run()
