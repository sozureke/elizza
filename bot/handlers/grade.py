import os
import asyncio
from aiogram import Router, types
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.grade_service import GradesService
from services.global_moodle_service import global_moodle_service
from keyboards.course import course_keyboard
from .course import courses_cache
from utils.delete import deletion_helper

grades_router = Router()
grades_cache = {}

gif_messages = {}  # Словарь для хранения message_id гифки

GIF_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "gif",
    "grades.gif.mp4"
)
GIF_PATH = os.path.normpath(GIF_PATH)

@grades_router.callback_query(lambda c: "course_" in c.data and "_grades" in c.data)
async def course_grades_handler(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        return

    course_idx = int(parts[1])
    course = courses_cache.get(course_idx)
    if not course:
        await callback.message.edit_text("Course not found.")
        return

    gif_message = None
    if os.path.exists(GIF_PATH):
        gif_file = FSInputFile(GIF_PATH)
        gif_message = await callback.message.answer_animation(animation=gif_file)
        deletion_helper.record_message(callback.message.chat.id, gif_message.message_id)
        gif_messages[course_idx] = gif_message.message_id

    await asyncio.sleep(2)

    service = GradesService(global_moodle_service.driver)
    grades_list = service.get_grades(course.link)
    grades_cache[course_idx] = grades_list

    if not grades_list:
        msg = await callback.message.edit_text(
            f"No grades found for {course.title}.",
            reply_markup=course_keyboard(course_idx)
        )
        deletion_helper.record_message(callback.message.chat.id, msg.message_id)
        return

    text = f"Grades for {course.title}:\n\n"
    for g in grades_list:
        text += f"{g.name} — {g.grade_value}\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="Hide Grades", callback_data=f"hide_grades_{course_idx}")
    kb.adjust(1)

    msg = await callback.message.edit_text(text, reply_markup=kb.as_markup())
    deletion_helper.record_message(callback.message.chat.id, msg.message_id)

@grades_router.callback_query(lambda c: c.data.startswith("hide_grades_"))
async def hide_grades_handler(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        return

    course_idx = int(parts[2])

    if course_idx in gif_messages:
        mid = gif_messages[course_idx]
        try:
            await callback.message.bot.delete_message(callback.message.chat.id, mid)
        except:
            pass
        del gif_messages[course_idx]

    await callback.message.delete()

    await callback.message.answer(
        "Grades closed. Returning to course menu:",
        reply_markup=course_keyboard(course_idx)
    )
    await callback.answer()
