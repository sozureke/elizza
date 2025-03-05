import re
import os
import json
import difflib
import logging
import nltk
import random
import requests
from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from services.grade_service import GradesService
from services.global_moodle_service import global_moodle_service
from services.assignment_service import AssignmentService

load_dotenv(dotenv_path="bot/.env.local")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class NLPProcessor:
    def __init__(self, courses_path="config/courses.json"):
        self.courses_path = courses_path
        self.keywords = {
            "grades": ["grade", "grades", "mark", "marks", "score", "result"],
            "assignments": ["assignment", "homework", "task", "exercise", "submission", "due"],
            "upcoming_assignment": ["next assignment", "upcoming homework", "soonest task", "nearest submission"],
            "joke": ["joke", "funny", "laugh"],
            "date": ["date", "today", "what day", "current date"],
            "weather": ["weather", "forecast", "temperature", "climate"],
            "greeting": ["hello", "hi", "hey", "greetings"],
            "howareyou": ["how are you", "how r you", "hru", "how you doing"],
            "farewell": ["bye", "goodbye", "see you", "farewell"],
            "funnygif": ["gif", "meme", "funny gif", "funny meme", "funny picture", "send me something funny"]
        }
        self.courses = self.load_courses()
        self.GIPHY_API_KEY = os.getenv("GIPHY_API")

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

    def detect_intent(self, text: str):
        text = self.normalize_text(text)
        for intent, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return intent
        return None

    def find_course(self, text: str):
        text = self.normalize_text(text)
        course_titles = [course["title"].lower() for course in self.courses]
        closest_match = difflib.get_close_matches(text, course_titles, n=1, cutoff=0.5)
        if closest_match:
            for course in self.courses:
                if course["title"].lower() == closest_match[0]:
                    return course
        return None

    def process_message(self, message: str):
        text = self.normalize_text(message)
        intent = self.detect_intent(text)
        if intent == "greeting":
            return self.respond_greeting()
        elif intent == "howareyou":
            return self.respond_howareyou()
        elif intent == "farewell":
            return self.respond_farewell()
        elif intent == "funnygif":
            return self.respond_funny_gif()
        if intent == "joke":
            return self.get_joke()
        elif intent == "date":
            return self.get_date()
        elif intent == "weather":
            return self.get_weather()
        if intent in ["grades", "assignments", "upcoming_assignment"]:
            course = self.find_course(text)
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
        return "🤖 I couldn't understand your request. You can ask about grades, assignments, jokes, date, weather, or just say 'hello'!"

    def respond_greeting(self):
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! Need anything?",
            "Hey! What's on your mind?",
            "Greetings, human! How may I assist?"
        ]
        return random.choice(greetings)

    def respond_howareyou(self):
        responses = [
            "I'm just a bot, but I'm feeling great, thanks for asking!",
            "Doing well, thanks! How about you?",
            "All good here in the digital realm!",
        ]
        return random.choice(responses)

    def respond_farewell(self):
        goodbyes = [
            "Bye! See you soon!",
            "Goodbye! Have a great day!",
            "Farewell, human!",
            "Take care! Come back soon."
        ]
        return random.choice(goodbyes)

    def respond_funny_gif(self):
        if not self.GIPHY_API_KEY or self.GIPHY_API_KEY.strip() == "":
            return "Here's a funny gif: https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif (No real Giphy API key provided.)"
        query = random.choice(["funny", "lol", "meme", "funny cat", "funny dog"])
        url = f"https://api.giphy.com/v1/gifs/search?api_key={self.GIPHY_API_KEY}&q={query}&limit=15"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            if "data" not in data or len(data["data"]) == 0:
                return "Sorry, I couldn't find a funny gif at the moment."
            gif_obj = random.choice(data["data"])
            gif_url = gif_obj["images"]["original"]["url"]
            return f"Here's a random GIF for you:\n{gif_url}"
        except Exception as e:
            logging.error(f"Giphy error: {e}")
            return "Oops, something went wrong fetching a GIF. Try again later."

    def get_joke(self):
        jokes = [
            "Why do Java developers wear glasses? Because they can't C#!",
            "I tried to catch fog yesterday. Mist!",
            "Why did the scarecrow get promoted? He was outstanding in his field!",
            "Why do programmers prefer dark mode? Because light attracts bugs!"
        ]
        return random.choice(jokes)

    def get_date(self):
        now = datetime.now()
        return now.strftime("Today is %A, %Y-%m-%d (%H:%M:%S)")

    def get_weather(self, city="London"):
        url = f"https://wttr.in/{city}?format=j1"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if "current_condition" not in data:
                return "I couldn't fetch the weather data. Please try again."
            current = data["current_condition"][0]
            temp_c = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            return f"The weather in {city} is {temp_c}°C with {desc}."
        except Exception as e:
            logging.error(f"Weather error: {e}")
            return "Sorry, I couldn't fetch the weather data at the moment."

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
