import pickle
import logging
from typing import Optional, List
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

class CookiesManager:
    @staticmethod
    def save_cookies(driver: WebDriver, file_path: str = "cookies.pkl") -> bool:
        try:
            cookies = driver.get_cookies()
            with open(file_path, "wb") as file:
                pickle.dump(cookies, file)
            logger.info(f"Cookies saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Cookie save error: {str(e)}")
            return False

    @staticmethod
    def load_cookies(driver: WebDriver, file_path: str = "cookies.pkl") -> bool:
        try:
            with open(file_path, "rb") as file:
                cookies: List[dict] = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            logger.info(f"Cookies loaded from {file_path}")
            return True
        except FileNotFoundError:
            logger.warning("Cookies file not found")
            return False
        except Exception as e:
            logger.error(f"Cookie load error: {str(e)}")
            return False