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

load_dotenv()

class MoodleService:
	def __init__(self) -> None:
			self.driver = None
			self.logged_in = False

	def init_driver(self) -> None:
			try:
					options = webdriver.ChromeOptions()
					options.add_argument("--no-sandbox")
					options.add_argument("--disable-dev-shm-usage")
					# options.add_argument("--headless")

					self.driver = webdriver.Chrome(
							service=Service(ChromeDriverManager().install()),
							options=options
					)
					self.driver.implicitly_wait(10)
					logger.info("The driver has been successfully initialised.")
			except Exception as e:
					logger.error(f"Driver initialisation error: {e}")
					raise

	def login(self, username: str, password: str) -> bool:
		if not self.driver:
			self.init_driver()

		try:
			MOODLE_URL = os.getenv("MOODLE_URL")
			if not MOODLE_URL:
				raise ValueError("MOODLE_URL environment variable is not set.")
			self.driver.get(MOODLE_URL)

			login_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary.btn-block")))
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
					lambda driver: "moodle.uni.lu/my/" in driver.current_url
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
					lambda driver: "sts.uni.lu/my.policy" in driver.current_url
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
		
	def human_type(self, element, text: str, delay: int=0.1) -> None:
		for character in text:
			element.send_keys(character)
			time.sleep(random.uniform(delay, delay))

	def close(self) -> None:
			if self.driver:
					self.driver.quit()
					logger.info("Driver closed.")