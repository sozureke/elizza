from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

def course_keyboard(course_idx: int) -> InlineKeyboardMarkup:
	kb_builder = InlineKeyboardBuilder()
	kb_builder.button(
		text="💌 News",
		callback_data=f"course_{course_idx}_news"
	)
	kb_builder.button(
		text="📕 Assignments",
		callback_data=f"course_{course_idx}_assignments"
	)
	kb_builder.button(
		text="📌 Grades",
		callback_data=f"course_{course_idx}_grades"
	)
	kb_builder.button(
		text="🔙 Back to courses",
		callback_data="courses_back"
	)
	kb_builder.adjust(1)
	return kb_builder.as_markup()