from services.global_moodle_service import MoodleService
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env.local")

def test_moodle_service():
    moodle = MoodleService()
    username = os.getenv("MOODLE_USERNAME")
    password = os.getenv("MOODLE_PASSWORD")

    if not username or not password:
        print("Убедитесь, что MOODLE_USERNAME и MOODLE_PASSWORD заданы в .env.")
        return

    if moodle.login(username, password):
        print("Авторизация успешна!")
    else:
        print("Ошибка авторизации.")

    moodle.close()

if __name__ == "__main__":
    test_moodle_service()