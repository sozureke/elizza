import asyncio
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from services.global_moodle_service import global_moodle_service
from keyboards.main_menu import main_menu_keyboard

auth_router = Router()

class AuthStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

@auth_router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    msg = await message.answer("Please enter your Moodle username:")
    await state.update_data(main_msg_id=msg.message_id)
    await state.set_state(AuthStates.waiting_for_username)

@auth_router.message(StateFilter(AuthStates.waiting_for_username))
async def process_username(message: types.Message, state: FSMContext):
    data = await state.get_data()
    main_msg_id = data.get("main_msg_id")
    await message.delete()
    await state.update_data(username=message.text)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=main_msg_id,
        text="Please enter your Moodle password:"
    )
    await state.set_state(AuthStates.waiting_for_password)

@auth_router.message(StateFilter(AuthStates.waiting_for_password))
async def process_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    main_msg_id = data.get("main_msg_id")
    username = data.get("username")
    password = message.text

    await message.delete()
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=main_msg_id,
        text="Logging in..."
    )

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, global_moodle_service.login, username, password)

    if result:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=main_msg_id,
            text="Logged in successfully!"
        )
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Use this menu to continue:",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=main_msg_id,
            text="Login failed. Please try /start again."
        )

    await state.clear()
