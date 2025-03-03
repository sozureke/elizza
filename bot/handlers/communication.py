from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_menu_keyboard, auth_keyboard
from services.global_moodle_service import global_moodle_service
from utils.delete import deletion_helper

communication_router = Router()

@communication_router.message(Command("start"))
async def greeting_handler(message: types.Message):
    deletion_helper.record_message(message.chat.id, message.message_id)
    if not global_moodle_service.logged_in:
        msg = await message.answer(
            "Welcome! Please authorize to continue.",
            reply_markup=auth_keyboard()
        )
        deletion_helper.record_message(message.chat.id, msg.message_id)
    else:
        msg = await message.answer(
            "You are already logged in. Use the menu below:",
            reply_markup=main_menu_keyboard()
        )
        deletion_helper.record_message(message.chat.id, msg.message_id)