from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Assignment:
    def __init__(self, name: str, due_date: str, submitted: bool, grade: str):
        self.name = name
        self.due_date = due_date
        self.submitted = submitted
        self.grade = grade

class AssignmentService:
    def __init__(self, driver):
        self.driver = driver

    def get_assignments(self, course_link: str) -> list[Assignment]:
        assignments = []
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
                assignments_link = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.dropdown-item[title='Assignments']"))
                )
                assignments_link.click()
            except TimeoutException:
                print("No 'Assignments' link found. Possibly no assignments in this course.")
                return assignments

            try:
                table = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.generaltable"))
                )
            except TimeoutException:
                print("Assignments table not found or empty.")
                return assignments

            rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
            for row in rows:
                if "tabledivider" in row.get_attribute("class"):
                    continue
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if len(cells) < 5:
                    continue

                assignment_name_elem = cells[1].find_element(By.TAG_NAME, "a")
                assignment_name = assignment_name_elem.text.strip()

                due_date = cells[2].text.strip()
                submission_text = cells[3].text.strip()
                submitted = "Submitted" in submission_text

                grade_text = cells[4].text.strip()
                grade = "No grade" if grade_text == "-" or not grade_text else grade_text

                assignments.append(Assignment(
                    name=assignment_name,
                    due_date=due_date,
                    submitted=submitted,
                    grade=grade
                ))

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error while loading or parsing assignments: {e}")
        return assignments
