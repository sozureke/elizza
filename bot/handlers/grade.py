from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.grade_service import GradesService
from services.global_moodle_service import global_moodle_service
from keyboards.course import course_keyboard
from .course import courses_cache
from utils.delete import deletion_helper

grades_router = Router()
grades_cache = {}

@grades_router.callback_query(lambda c: "course_" in c.data and "_grades" in c.data)
async def course_grades_handler(callback: types.CallbackQuery):
    await callback.answer("Loading grades...")
    deletion_helper.record_message(callback.message.chat.id, callback.message.message_id)

    parts = callback.data.split("_")
    if len(parts) < 3:
        return

    course_idx = int(parts[1])
    course = courses_cache.get(course_idx)
    if not course:
        await callback.message.edit_text("Course not found.")
        return

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
    kb.button(text="Back to course", callback_data=f"course_{course_idx}")
    kb.adjust(1)

    msg = await callback.message.edit_text(
        text,
        reply_markup=kb.as_markup()
    )
    deletion_helper.record_message(callback.message.chat.id, msg.message_id)

