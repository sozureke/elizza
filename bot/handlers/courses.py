from aiogram import Router, types
from services.course_service import CourseService
from services.global_moodle_service import global_moodle_service
from aiogram.utils.keyboard import InlineKeyboardBuilder

course_router = Router()

@course_router.message(lambda msg: msg.text == "📚 My courses")
async def courses_handler(message: types.Message):
    await message.delete()
    loading_msg = await message.answer("Loading courses...")

    if not global_moodle_service.logged_in or not global_moodle_service.driver:
        await loading_msg.edit_text("You're not logged in yet. Please authorize first.")
        return

    course_service = CourseService(global_moodle_service.driver)
    courses = course_service.get_courses()

    if not courses:
        await loading_msg.edit_text("No courses found.")
        return

    kb_builder = InlineKeyboardBuilder()
    for idx, c in enumerate(courses, start=1):
        kb_builder.button(
            text=c.title,
            callback_data=f"course_{idx}"
        )
    kb_builder.adjust(1)

    await loading_msg.edit_text(
        "Available courses (choose one):",
        reply_markup=kb_builder.as_markup()
    )

