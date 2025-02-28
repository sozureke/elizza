from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.course_service import CourseService
from services.global_moodle_service import global_moodle_service
from services.assignment_service import AssignmentService
from keyboards.course import course_keyboard

course_router = Router()
courses_cache = {}

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

    courses_cache.clear()
    for idx, c in enumerate(courses, start=1):
        courses_cache[idx] = c

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

@course_router.callback_query(lambda c: "course_" in c.data and any(x in c.data for x in ["_news","_assignments","_grades"]))
async def course_action_handler(callback: types.CallbackQuery):
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
    elif action == "assignments":
        assignment_service = AssignmentService(global_moodle_service.driver)
        assignments = assignment_service.get_assignments(course.link)

        if assignments:
            text = f"Assignments for {course.title}:\n\n"
            for i, a in enumerate(assignments, start=1):
                text += f"{i}. {a.name}\n"
                text += f"   Due: {a.due_date}\n"
                text += f"   Submitted: {'Yes' if a.submitted else 'No'}\n"
                text += f"   Grade: {a.grade}\n\n"
        else:
            text = f"No assignments found for {course.title}."
    elif action == "grades":
        text = f"Grades for {course.title}:\n(Here parse and display grades...)"
    else:
        text = "Unknown action."

    await callback.message.edit_text(
        text,
        reply_markup=course_keyboard(course_idx)
    )
    await callback.answer()

@course_router.callback_query(lambda c: c.data.startswith("course_") and "_" not in c.data[7:])
async def selected_course_handler(callback: types.CallbackQuery) -> None:
    course_idx = int(callback.data.split("_")[1])
    selected_course = courses_cache.get(course_idx)
    if not selected_course:
        await callback.edit_text("No courses found. Try again later.")
        return
    await callback.message.edit_text(
        f"Course selected: {selected_course.title}\nChoose an action:",
        reply_markup=course_keyboard(course_idx)
    )
    await callback.answer()

@course_router.callback_query(lambda cq: cq.data == "courses_back")
async def courses_back_handler(callback: types.CallbackQuery):
    if not courses_cache:
        await callback.message.edit_text("No cached courses. Try /start again.")
        return

    kb_builder = InlineKeyboardBuilder()
    for idx, c in courses_cache.items():
        kb_builder.button(
            text=c.title,
            callback_data=f"course_{idx}"
        )
    kb_builder.adjust(1)

    await callback.message.edit_text(
        "Available courses (choose one):",
        reply_markup=kb_builder.as_markup()
    )
    await callback.answer()
