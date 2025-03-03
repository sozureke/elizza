from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Grade:
    def __init__(self, name: str, link: str, item_type: str, grade_value: str):
        self.name = name
        self.link = link
        self.item_type = item_type
        self.grade_value = grade_value

class GradesService:
    def __init__(self, driver):
        self.driver = driver

    def get_grades(self, course_link: str) -> list[Grade]:
        grades = []
        try:
            self.driver.get(course_link)
            menu_container = self.driver.find_element(
                By.CSS_SELECTOR, "div.navbar.navbar-expand.btco-hover-menu"
            )

            dropdown_li = menu_container.find_element(
                By.CSS_SELECTOR, "li.nav-item.dropdown.my-auto"
            )
            this_course_link = dropdown_li.find_element(
                By.CSS_SELECTOR, "a.nav-link.dropdown-toggle.my-auto"
            )
            this_course_link.click()

            try:
                grades_link = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.dropdown-item[title='Grades']"))
                )
                grades_link.click()
            except TimeoutException:
                print("No 'Grades' link found. Possibly no grades in this course.")
                return grades

            try:
                table = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.generaltable boxaligncenter user-grade")
                    )
                )
            except TimeoutException:
                print("Grades table not found or empty.")
                return grades

            rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
            for row in rows:
                try:
                    th_elem = row.find_element(By.CSS_SELECTOR, "th.level3.item.b1b.column-itemname")
                    item_type = ""
                    try:
                        item_type_span = th_elem.find_element(By.CSS_SELECTOR, "span.d-block.text-uppercase.small.dimmed_text")
                        item_type = item_type_span.get_attribute("title")
                    except NoSuchElementException:
                        pass
                    name_link_elem = th_elem.find_element(By.CSS_SELECTOR, "div.rowtitle a.gradeitemheader")
                    name = name_link_elem.text.strip()
                    link = name_link_elem.get_attribute("href")
                    tds = row.find_elements(By.CSS_SELECTOR, "td")
                    grade_value = ""
                    if tds:
                        grade_value = tds[-1].text.strip()
                    grades.append(Grade(name, link, item_type, grade_value))

                except NoSuchElementException:
                    continue

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error while loading or parsing grades: {e}")

        return grades
