from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.assignment_service import AssignmentService
from services.global_moodle_service import global_moodle_service
from keyboards.course import course_keyboard


assignments_cache = {}
assignments_router = Router()

@assignments_router.callback_query(lambda c: "course_" in c.data and "_assignments" in c.data)
async def course_assignments_handler(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Invalid action.")
        return

    course_idx = int(parts[1])
    from .courses import courses_cache
    course = courses_cache.get(course_idx)
    if not course:
        await callback.answer("Course not found.")
        return

    assignment_service = AssignmentService(global_moodle_service.driver)
    assignments = assignment_service.get_assignments(course.link)
    assignments_cache[course_idx] = assignments

    if not assignments:
        text = f"No assignments found for {course.title}."
        await callback.message.edit_text(
            text,
            reply_markup=course_keyboard(course_idx)
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    for i, a in enumerate(assignments, start=1):
        builder.button(
            text=a.name,
            callback_data=f"assignment_{course_idx}_{i}"
        )
    builder.button(
        text="Back to course",
        callback_data=f"course_{course_idx}"
    )
    builder.adjust(1)

    await callback.message.edit_text(
        f"Assignments for {course.title}:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@assignments_router.callback_query(lambda c: c.data.startswith("assignment_"))
async def assignment_detail_handler(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Invalid assignment data.")
        return

    course_idx = int(parts[1])
    assign_idx = int(parts[2])

    assignment_list = assignments_cache.get(course_idx, [])
    if not assignment_list or assign_idx < 1 or assign_idx > len(assignment_list):
        await callback.answer("Assignment not found.")
        return

    assignment = assignment_list[assign_idx - 1]

    text = (
        f"<b>{assignment.name}</b>\n\n"
        f"Due date: {assignment.due_date}\n"
        f"Submitted: {'Yes' if assignment.submitted else 'No'}\n"
        f"Grade: {assignment.grade}\n\n"
        "If you want to upload a file, click the button below.\n"
        "(Currently not implemented via Selenium.)"
    )

    builder = InlineKeyboardBuilder()
    if assignment.link:
        builder.button(
            text="Open assignment",
            url=assignment.link
        )

    if not assignment.submitted:
        builder.button(
            text="Upload file",
            callback_data=f"upload_{course_idx}_{assign_idx}"
        )

    builder.button(
        text="Back to assignments",
        callback_data=f"course_{course_idx}_assignments"
    )

    builder.adjust(1)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# TODO
@assignments_router.callback_query(lambda c: c.data.startswith("upload_"))
async def upload_file_handler(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Invalid upload data.")
        return

    await callback.message.edit_text(
        "File upload via bot is not implemented yet. Please use Moodle in your browser."
    )
    await callback.answer()
