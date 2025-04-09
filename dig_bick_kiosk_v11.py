import time
import json
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.config_mtime = None
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
        chrome_options.add_argument("--kiosk")  # Uncomment after testing
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

        self.attempt_sign_in()

    def attempt_sign_in(self):
        try:
            wait = WebDriverWait(self.driver, 15)
            sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))

            if sign_in_button:
                self.log("[INFO] Sign-in button detected and clickable. Attempting click...")
                try:
                    sign_in_button.click()
                    self.log("[INFO] Clicked sign-in button successfully.")
                except Exception as e:
                    self.log(f"[WARN] Normal click failed: {e}. Attempting JS click...")
                    try:
                        self.driver.execute_script("arguments[0].click();", sign_in_button)
                        self.log("[INFO] JS click on sign-in button successful.")
                    except Exception as js_error:
                        self.log(f"[ERROR] JS click also failed: {js_error}")
            else:
                self.log("[INFO] Sign-in button was not clickable.")
        except Exception as e:
            self.log(f"[INFO] Sign-in button not found or not clickable within timeout: {e}")

    def cycle_tabs(self):
        while not self.stop_event.wait(self.cycle_delay):
            try:
                self.driver.switch_to.window(self.driver.window_handles[self.current_tab])
                self.driver.refresh()
                self.current_tab = (self.current_tab + 1) % len(self.driver.window_handles)
                self.log(f"[INFO] Switched to tab {self.current_tab}")
            except Exception as e:
                self.log(f"[ERROR] Error during tab cycling: {e}")

    def listen_for_exit(self):
        def on_press(key):
            try:
                if key == keyboard.HotKey.parse('<ctrl>+<shift>+q').keys[-1]:
                    self.log("[INFO] Exit hotkey pressed. Exiting...")
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
