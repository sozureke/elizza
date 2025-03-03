import re
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

def parse_course_id(url: str) -> int:
    match = re.search(r"id=(\d+)", url)
    if match:
        return int(match.group(1))
    return -1


class GradesService:
    def __init__(self, driver):
        self.driver = driver
        self.driver.implicitly_wait(0)

    def get_grades(self, course_link: str) -> list[Grade]:
        grades = []
        new_course_id = parse_course_id(course_link)
        try:
            current_url = self.driver.current_url
            current_course_id = parse_course_id(current_url)
            if ("grade/report" not in current_url) or (new_course_id != current_course_id):
                self.driver.get(course_link)

                try:
                    menu_container = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div.navbar.navbar-expand.btco-hover-menu")
                        )
                    )
                except TimeoutException:
                    print("Menu container not found quickly.")
                    return grades

                try:
                    dropdown_li = menu_container.find_element(
                        By.CSS_SELECTOR, "li.nav-item.dropdown.my-auto"
                    )
                    nav_link = dropdown_li.find_element(
                        By.CSS_SELECTOR, "a.nav-link.dropdown-toggle.my-auto"
                    )
                    nav_link.click()
                except NoSuchElementException:
                    print("Could not find 'This course' dropdown.")
                    return grades

                try:
                    grades_link = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "a.dropdown-item[title='Grades']")
                        )
                    )
                    grades_link.click()
                except TimeoutException:
                    print("No 'Grades' link found or not clickable.")
                    return grades

            try:
                table = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.generaltable.boxaligncenter.user-grade")
                    )
                )
            except TimeoutException:
                print("Grades table not found or empty.")
                return grades

            rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")

            for row in rows:
                try:
                    th_elem = row.find_element(
                        By.CSS_SELECTOR,
                        "th.level1.item.b1b.column-itemname,"
                        "th.level2.item.b1b.column-itemname,"
                        "th.level3.item.b1b.column-itemname"
                    )
                except NoSuchElementException:
                    continue

                try:
                    name_link_elem = th_elem.find_element(
                        By.CSS_SELECTOR, "a.gradeitemheader"
                    )
                except NoSuchElementException:
                    continue

                name = name_link_elem.text.strip()
                link = name_link_elem.get_attribute("href") or ""

                item_type = ""
                try:
                    type_span = th_elem.find_element(
                        By.CSS_SELECTOR,
                        "span.d-block.text-uppercase.small.dimmed_text"
                    )
                    item_type = type_span.get_attribute("title") or ""
                except NoSuchElementException:
                    pass

                grade_value = ""
                try:
                    grade_td = row.find_element(
                        By.CSS_SELECTOR, "td.column-grade.cell.c2"
                    )
                    grade_value = grade_td.text.strip()
                except NoSuchElementException:
                    tds = row.find_elements(By.CSS_SELECTOR, "td")
                    if tds:
                        grade_value = tds[-1].text.strip()

                grades.append(Grade(name, link, item_type, grade_value))

        except Exception as e:
            print(f"Error parsing grades: {e}")

        return grades
