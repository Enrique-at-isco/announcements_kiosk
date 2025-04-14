import time
import json
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pynput import keyboard

CONFIG_FILE = '/home/annkiosk/announcements_kiosk/pipiosk_v1/config.json'
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

class KioskController:
    def __init__(self):
        self.driver = None
        self.urls = []
        self.current_tab = 0
        self.cycle_delay = 10  # default
        self.stop_event = threading.Event()
        self.load_config()

    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

            urls = config.get('urls', [])
            if not urls or not all(isinstance(url, str) and url.strip() for url in urls):
                raise ValueError("Config error: All URLs must be non-empty strings!")

            self.urls = urls
            self.cycle_delay = config.get('cycle_delay', self.cycle_delay)

            self.log(f"[INFO] Loaded config: {config}")
        except Exception as e:
            self.log(f"[ERROR] Error loading config: {e}")

    def start_browser(self):
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        chrome_options.add_argument("--user-data-dir=/home/annkiosk/.config/chromium")
        chrome_options.add_argument("--profile-directory=Default")
        # chrome_options.add_argument("--kiosk")  # Uncomment after testing
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--allow-file-access-from-files")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--use-gl=swiftshader")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")

        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open the first URL
        self.driver.get(self.urls[0])

        # Open remaining URLs in new tabs
        for url in self.urls[1:]:
            self.driver.execute_script(f"window.open('{url}', '_blank');")

        # Initial login attempt at startup
        self.auto_click_sign_in()
        # Close any about:blank tabs at startup
        self.close_about_blank_tabs()

    def auto_click_sign_in(self):
        try:
            self.driver.switch_to.frame(0)
            for attempt in range(5):
                try:
                    sign_in_span = self.driver.find_element(By.CSS_SELECTOR, "span[data-bind='text:actionText']")
                    sign_in_button = sign_in_span.find_element(By.XPATH, "./ancestor::button")
                    self.driver.execute_script("arguments[0].click();", sign_in_button)
                    self.log("[INFO] Auto-clicked sign-in button.")
                    break
                except Exception:
                    time.sleep(1)
        except Exception as e:
            self.log(f"[INFO] No sign-in frame/button found: {e}")
        finally:
            self.driver.switch_to.default_content()

    def close_about_blank_tabs(self):
        original_handle = self.driver.current_window_handle
        handles = self.driver.window_handles.copy()
        for handle in handles:
            try:
                self.driver.switch_to.window(handle)
                if self.driver.current_url == 'about:blank':
                    self.driver.close()
                    self.log("[INFO] Closed about:blank tab.")
            except Exception as e:
                self.log(f"[WARN] Failed to close about:blank tab: {e}")
        self.driver.switch_to.window(original_handle)

    def cycle_tabs(self):
        while not self.stop_event.wait(self.cycle_delay):
            try:
                if not self.driver.window_handles:
                    self.log("[WARN] No open tabs found. Exiting tab cycle.")
                    break

                self.current_tab = self.current_tab % len(self.driver.window_handles)
                self.driver.switch_to.window(self.driver.window_handles[self.current_tab])
                self.log(f"[INFO] Switched to tab {self.current_tab + 1}/{len(self.driver.window_handles)}: {self.driver.current_url}")

                # Check if sign-in is needed on this tab
                self.auto_click_sign_in()
                self.close_about_blank_tabs()

                self.current_tab += 1
            except Exception as e:
                self.log(f"[ERROR] Error during tab cycling: {e}")

    def listen_for_exit(self):
        def on_press(key):
            try:
                if key == keyboard.Key.esc and keyboard.Controller().ctrl_pressed:
                    self.log("[INFO] Exit hotkey (Ctrl+Esc) pressed. Exiting...")
                    self.stop_event.set()
                    return False
            except AttributeError:
                pass

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def run(self):
        self.log("[INFO] Starting browser with Selenium...")
        self.start_browser()

        threading.Thread(target=self.cycle_tabs, daemon=True).start()
        threading.Thread(target=self.listen_for_exit, daemon=True).start()

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
