from selenium.webdriver.common.by import By

class Course:
	def __init__(self, title: str, link: str):
		self.title = title
		self.link = link
		self.homeworks = []
		self.news = []
		self.grades = []

class CourseService:
	def __init__(self, driver):
		self.driver = driver

	def get_courses(self) -> list:
		deck_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card-deck.dashboard-card-deck")
		courses = []
		for deck in deck_elements:
			cards = deck.find_elements(By.CSS_SELECTOR, "div.card.dashboard-card[data-region='course-content']")
			for card in cards:
				try:
					title_elem = card.find_element(By.CSS_SELECTOR, "span.multiline")
					title = title_elem.get_attribute("title")
					link = title_elem.get_attribute("href")
					courses.append(Course(title, link))
				except Exception as error:
					print("Error parsing card:", error)
		return courses