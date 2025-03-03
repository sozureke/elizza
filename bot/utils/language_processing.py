import re
import json
import difflib
import logging
import nltk
from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.grade_service import GradesService
from services.global_moodle_service import global_moodle_service
from services.assignment_service import AssignmentService

nltk.download("punkt_tab")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class NLPProcessor:
    def __init__(self, courses_path="config/courses.json"):
        self.courses_path = courses_path
        self.keywords = {
            "grades": ["grade", "grades", "mark", "marks", "score", "result"],
            "assignments": ["assignment", "homework", "task", "exercise", "submission", "due"],
            "upcoming_assignment": ["next assignment", "upcoming homework", "soonest task", "nearest submission"]
        }
        self.courses = self.load_courses()

    def load_courses(self):
        try:
            with open(self.courses_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning("⚠️ Course file not found!")
            return []

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        tokens = nltk.word_tokenize(text)
        return " ".join(tokens)

    def find_course(self, text: str):
        text = self.normalize_text(text)
        course_titles = [course["title"].lower() for course in self.courses]
        closest_match = difflib.get_close_matches(text, course_titles, n=1, cutoff=0.5)

        if closest_match:
            for course in self.courses:
                if course["title"].lower() == closest_match[0]:
                    return course
        return None

    def detect_intent(self, text: str):
        text = self.normalize_text(text)
        words = text.split()

        for intent, keywords in self.keywords.items():
            for keyword in keywords:
                if any(re.search(rf"\b{re.escape(keyword)}\b", word) for word in words):
                    return intent
        return None

    def process_message(self, message: str):
        text = self.normalize_text(message)
        intent = self.detect_intent(text)
        course = self.find_course(text)

        if not intent:
            return "🤖 I couldn't understand your request. Please specify grades or assignments."

        if not course:
            return "❌ I couldn't find this course in your list. Please check the course name."

        course_title = course["title"]
        course_link = course["link"]

        logging.info(f"📌 Detected intent: {intent} for course: {course_title}")

        if intent == "grades":
            return self.get_grades(course_title, course_link)
        elif intent == "assignments":
            return self.get_assignments(course_title, course_link)
        elif intent == "upcoming_assignment":
            return self.get_upcoming_assignment(course_title, course_link)

    def get_grades(self, course_title, course_link):
        service = GradesService(global_moodle_service.driver)
        grades = service.get_grades(course_link)

        if not grades:
            return f"📌 No grades found for {course_title}."

        response = f"📊 *Grades for {course_title}:*\n\n"
        for grade in grades:
            response += f"📌 {grade.name}: {grade.grade_value}\n"
        return response

    def get_assignments(self, course_title, course_link):
        service = AssignmentService(global_moodle_service.driver)
        assignments = service.get_assignments(course_link)

        if not assignments:
            return f"📌 No assignments found for {course_title}."

        builder = InlineKeyboardBuilder()
        for i, assignment in enumerate(assignments, start=1):
            builder.button(
                text=f"{assignment.name} (Due: {assignment.due_date})",
                callback_data=f"assignment_{course_title}_{i}"
            )
        builder.adjust(1)

        return {
            "text": f"📌 Assignments for {course_title}:",
            "reply_markup": builder.as_markup()
        }

    def get_upcoming_assignment(self, course_title, course_link):
        service = AssignmentService(global_moodle_service.driver)
        assignments = service.get_assignments(course_link)

        if not assignments:
            return f"📌 No upcoming assignments found for {course_title}."

        now = datetime.now()
        upcoming_assignments = sorted(
            (a for a in assignments if datetime.strptime(a.due_date, "%Y-%m-%d") >= now),
            key=lambda x: datetime.strptime(x.due_date, "%Y-%m-%d")
        )

        if not upcoming_assignments:
            return f"📌 No upcoming assignments for {course_title}."

        closest_assignment = upcoming_assignments[0]

        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{closest_assignment.name} (Due: {closest_assignment.due_date})",
            callback_data=f"assignment_{course_title}_1"
        )
        builder.adjust(1)

        return {
            "text": f"📌 Next assignment for {course_title}:",
            "reply_markup": builder.as_markup()
        }
