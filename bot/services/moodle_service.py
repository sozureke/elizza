import os
import time
import random
import logging
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(dotenv_path=".env.local")

class MoodleService:
	def __init__(self) -> None:
		self.driver = None
		self.logged_in = False

	def init_driver(self) -> None:
		try:
			options = webdriver.ChromeOptions()
			options.add_argument("--no-sandbox")
			options.add_argument("--disable-dev-shm-usage")
			user_data_dir = os.path.abspath("chrome_profile")
			options.add_argument(f"user-data-dir={user_data_dir}")
			# options.add_argument("--headless")
			self.driver = webdriver.Chrome(
				service=Service(ChromeDriverManager().install()),
				options=options
			)
			self.driver.implicitly_wait(10)
			logger.info("Driver initialised.")
		except Exception as e:
			logger.error(f"Driver init error: {e}")
			raise

	def login(self, username: str, password: str) -> bool:
		if self.logged_in and self.driver:
			logger.info("Already logged in, skipping login.")
			return True

		if not self.driver:
			self.init_driver()

		try:
			MOODLE_URL = os.getenv("MOODLE_URL")
			if not MOODLE_URL:
				raise ValueError("MOODLE_URL not set.")

			self.driver.get(MOODLE_URL)
			if "moodle.uni.lu/my/" in self.driver.current_url:
				logger.info("Already logged in (session restored).")
				self.logged_in = True
				return True

			login_button = WebDriverWait(self.driver, 10).until(
				EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary.btn-block"))
			)
			login_button.click()

			try:
				WebDriverWait(self.driver, 15).until(
					EC.presence_of_element_located((By.ID, "auth_form"))
				)
				username_field = WebDriverWait(self.driver, 15).until(
					EC.visibility_of_element_located((By.ID, "input_1"))
				)
				password_field = WebDriverWait(self.driver, 15).until(
					EC.visibility_of_element_located((By.ID, "input_2"))
				)
				self.human_type(username_field, username)
				self.human_type(password_field, password)
				password_field.send_keys(Keys.RETURN)
				WebDriverWait(self.driver, 10).until(
					lambda d: "moodle.uni.lu/my/" in d.current_url
				)
				self.logged_in = True
				return True
			except (TimeoutException, NoSuchElementException):
				logger.info("Login form not found. Trying alert...")

			try:
				WebDriverWait(self.driver, 10).until(EC.alert_is_present())
				alert = self.driver.switch_to.alert
				alert.send_keys(username)
				alert.send_keys("\t")
				alert.send_keys(password)
				alert.accept()
				WebDriverWait(self.driver, 10).until(
					lambda d: "sts.uni.lu/my.policy" in d.current_url
				)
				self.logged_in = True
				logger.info("Login via alert successful.")
				return True
			except (TimeoutException, NoSuchElementException) as error:
				logger.error(f"Login via alert failed: {error}")
				return False
		except Exception as e:
			logger.error(f"Unexpected error: {e}")
			return False

	def human_type(self, element, text: str, delay: float=0.1) -> None:
		for ch in text:
			element.send_keys(ch)
			time.sleep(random.uniform(delay, delay))

	def close(self) -> None:
		if self.driver:
			self.driver.quit()
			logger.info("Driver closed.")
