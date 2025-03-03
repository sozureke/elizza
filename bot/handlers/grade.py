from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.grade_service import GradesService
from services.global_moodle_service import global_moodle_service
from keyboards.course import course_keyboard
from .course import courses_cache

grades_router = Router()
grades_cache = {}

@grades_router.callback_query(lambda c: "course_" in c.data and "_grades" in c.data)
async def course_grades_handler(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Invalid action.")
        return

    course_idx = int(parts[1])
    course = courses_cache.get(course_idx)
    if not course:
        await callback.answer("Course not found.")
        return

    service = GradesService(global_moodle_service.driver)
    grades_list = service.get_grades(course.link)
    grades_cache[course_idx] = grades_list

    if not grades_list:
        text = f"No grades found for {course.title}."
        await callback.message.edit_text(text, reply_markup=course_keyboard(course_idx))
        await callback.answer()
        return

    text = f"Grades for {course.title}:\n\n"
    for g in grades_list:
        text += f"- {g.name} ({g.item_type}): {g.grade_value}\n"

    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(
        text="Back to course",
        callback_data=f"course_{course_idx}"
    )
    kb_builder.adjust(1)

    await callback.message.edit_text(
        text,
        reply_markup=kb_builder.as_markup()
    )
    await callback.answer()
