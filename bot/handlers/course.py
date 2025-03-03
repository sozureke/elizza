from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.course_service import CourseService
from services.global_moodle_service import global_moodle_service
from keyboards.course import course_keyboard
from utils.delete import deletion_helper

course_router = Router()
courses_cache = {}

@course_router.message(lambda msg: msg.text == "📚 My courses")
async def courses_handler(message: types.Message):
    deletion_helper.record_message(message.chat.id, message.message_id)
    await message.delete()

    loading_msg = await message.answer("Loading courses...")
    deletion_helper.record_message(message.chat.id, loading_msg.message_id)

    if not global_moodle_service.logged_in or not global_moodle_service.driver:
        await loading_msg.edit_text("You're not logged in yet. Please authorize first.")
        return

    course_service = CourseService(global_moodle_service.driver)
    courses = course_service.get_courses()
    if not courses:
        await loading_msg.edit_text("No courses found.")
        return

    courses_cache.clear()
    for idx, c in enumerate(courses, start=1):
        courses_cache[idx] = c

    kb_builder = InlineKeyboardBuilder()
    for idx, c in enumerate(courses, start=1):
        kb_builder.button(text=c.title, callback_data=f"course_{idx}")
    kb_builder.adjust(1)

    await loading_msg.edit_text(
        "Available courses (choose one):",
        reply_markup=kb_builder.as_markup()
    )

@course_router.callback_query(lambda c: c.data.startswith("course_") and "_" not in c.data[7:])
async def selected_course_handler(callback: types.CallbackQuery):
    deletion_helper.record_message(callback.message.chat.id, callback.message.message_id)

    course_idx = int(callback.data.split("_")[1])
    selected_course = courses_cache.get(course_idx)
    if not selected_course:
        await callback.message.edit_text("No courses found. Try again later.")
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Course selected: {selected_course.title}\nChoose an action:",
        reply_markup=course_keyboard(course_idx)
    )
    await callback.answer()

@course_router.callback_query(lambda c: "course_" in c.data and "_news" in c.data)
async def course_action_handler(callback: types.CallbackQuery):
    deletion_helper.record_message(callback.message.chat.id, callback.message.message_id)

    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Invalid action.")
        return

    course_idx = int(parts[1])
    action = parts[2]
    course = courses_cache.get(course_idx)
    if not course:
        await callback.answer("Course not found.")
        return

    if action == "news":
        text = f"News for {course.title}:\n(Here parse and display news...)"
    else:
        text = "Unknown action."

    await callback.message.edit_text(text, reply_markup=course_keyboard(course_idx))
    await callback.answer()

@course_router.callback_query(lambda cq: cq.data == "courses_back")
async def courses_back_handler(callback: types.CallbackQuery):
    deletion_helper.record_message(callback.message.chat.id, callback.message.message_id)

    if not courses_cache:
        await callback.message.edit_text("No cached courses. Try /start again.")
        await callback.answer()
        return

    kb_builder = InlineKeyboardBuilder()
    for idx, c in courses_cache.items():
        kb_builder.button(text=c.title, callback_data=f"course_{idx}")
    kb_builder.adjust(1)

    await callback.message.edit_text(
        "Available courses (choose one):",
        reply_markup=kb_builder.as_markup()
    )
    await callback.answer()
