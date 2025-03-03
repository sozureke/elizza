import asyncio
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from services.global_moodle_service import global_moodle_service
from keyboards.main_menu import main_menu_keyboard, auth_keyboard
from utils.delete import deletion_helper

auth_router = Router()

class AuthStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

@auth_router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)
    msg = await message.answer("Please enter your Moodle username:")
    deletion_helper.record_message(message.chat.id, msg.message_id)
    await state.set_state(AuthStates.waiting_for_username)

@auth_router.message(lambda m: m.text == "🔑 Authorize")
async def authorize_button(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)
    msg = await message.answer("Please enter your Moodle username:")
    deletion_helper.record_message(message.chat.id, msg.message_id)
    await state.set_state(AuthStates.waiting_for_username)

@auth_router.message(StateFilter(AuthStates.waiting_for_username))
async def process_username(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)
    await message.delete()
    msg_id = await edit_or_create(message, "Please enter your Moodle password:")
    deletion_helper.record_message(message.chat.id, msg_id)
    await state.update_data(username=message.text)
    await state.set_state(AuthStates.waiting_for_password)

@auth_router.message(StateFilter(AuthStates.waiting_for_password))
async def process_password(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)
    await message.delete()
    msg_id = await edit_or_create(message, "Logging in...")
    deletion_helper.record_message(message.chat.id, msg_id)
    data = await state.get_data()
    username = data.get("username")
    password = message.text
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, global_moodle_service.login, username, password)
    if result:
        await edit_or_create(message, "Logged in successfully!", msg_id)
        m = await message.answer("Use this menu to continue:", reply_markup=main_menu_keyboard())
        deletion_helper.record_message(message.chat.id, m.message_id)
    else:
        await edit_or_create(message, "Login failed. Please try again.", msg_id)
    await state.clear()

@auth_router.message(lambda m: m.text == "🚪 Log out")
async def logout_handler(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)
    await deletion_helper.delete_all(message.chat.id, message.bot)
    m = await message.answer("You have been logged out.", reply_markup=auth_keyboard())
    deletion_helper.record_message(message.chat.id, m.message_id)
    await state.clear()

async def edit_or_create(message: types.Message, text: str, msg_id: int=None) -> int:
    if msg_id:
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=msg_id
        )
        return msg_id
    else:
        msg = await message.answer(text)
        return msg.message_id
