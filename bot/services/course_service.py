import os
import re
import json
from selenium.webdriver.common.by import By

class Course:
	def __init__(self, title: str, link: str):
		self.title = title
		self.link = link
		self.homeworks = []
		self.news = []
		self.grades = []

	def to_dict(self):
		return {"title": self.title, "link": self.link}

class CourseService:
	def __init__(self, driver):
		self.driver = driver
		self.config_path = "config/courses.json"

	def get_courses(self) -> list:
		deck_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.card-deck.dashboard-card-deck")
		courses = []
		for deck in deck_elements:
			cards = deck.find_elements(By.CSS_SELECTOR, "div.card.dashboard-card[data-region='course-content']")
			for card in cards:
				try:
					title_elem = card.find_element(By.CSS_SELECTOR, "span.multiline")
					link_elem = card.find_element(By.CSS_SELECTOR, "a.aalink.coursename")
					title = title_elem.get_attribute("title")
					link = link_elem.get_attribute("href")
					if link:
						courses.append(Course(title, link))
				except Exception as error:
					print("Error parsing card:", error)
		self.save_courses_to_json(courses)
		return courses

	def get_courses_dict(self) -> dict:
		courses = self.get_courses()
		return {course.title.lower().strip(): self.extract_course_id(self, course.link) for course in courses}

	def save_courses_to_json(self, courses: list[Course]):
		os.makedirs("config", exist_ok=True)
		courses_data = [course.to_dict() for course in courses]
		with open(self.config_path, "w", encoding="utf-8") as file:
			json_string = json.dumps(courses_data, indent=4, ensure_ascii=False)
			file.write(json_string)

	@staticmethod
	def extract_course_id(self, link: str) -> int:
		match = re.search(r"id=(\d+)", link)
		if match:
			return int(match.group(1))
		return -1
