import asyncio
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from services.moodle_service import MoodleService
from aiogram.filters.state import State, StatesGroup
from keyboards.main_menu import auth_keyboard, main_menu_keyboard

auth_router = Router()
moodle_service = MoodleService()

class AuthStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

@auth_router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext) -> None:
    await asyncio.sleep(2)
    await message.delete()
    bot_msg = await message.answer("Hi! Please log in.", reply_markup=auth_keyboard())
    await state.set_state(AuthStates.waiting_for_username)
    await state.set_data({"delete_ids": [{"chat_id": message.chat.id, "message_id": bot_msg.message_id}]})

@auth_router.message(lambda message: message.text == "🔑 Authorize")
async def auth_start(message: types.Message, state: FSMContext) -> None:
    await asyncio.sleep(2)
    await message.delete()
    bot_msg = await message.answer("Enter your username:")
    await state.set_state(AuthStates.waiting_for_username)
    await state.set_data({"delete_ids": [{"chat_id": message.chat.id, "message_id": bot_msg.message_id}]})

@auth_router.message(StateFilter(AuthStates.waiting_for_username))
async def process_username(message: types.Message, state: FSMContext):
    await asyncio.sleep(2)
    await message.delete()
    await state.update_data(username=message.text)
    bot_msg = await message.answer("Enter your password:")
    data = await state.get_data()
    delete_ids = data.get("delete_ids", [])
    delete_ids.append({"chat_id": message.chat.id, "message_id": bot_msg.message_id})
    await state.update_data(delete_ids=delete_ids)
    await state.set_state(AuthStates.waiting_for_password)

@auth_router.message(StateFilter(AuthStates.waiting_for_password))
async def process_password(message: types.Message, state: FSMContext):
    await asyncio.sleep(2)
    await message.delete()
    data = await state.get_data()
    username = data.get("username")
    password = message.text
    progress_msg = await message.answer("Please wait, authorisation is in progress...")
    data = await state.get_data()
    delete_ids = data.get("delete_ids", [])
    delete_ids.append({"chat_id": message.chat.id, "message_id": progress_msg.message_id})
    await state.update_data(delete_ids=delete_ids)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, moodle_service.login, username, password)
    if result:
        await message.answer("Authorisation was successful!", reply_markup=main_menu_keyboard())
    else:
        error_msg = await message.answer("Authorisation error. Try again.", reply_markup=auth_keyboard())
        data = await state.get_data()
        delete_ids = data.get("delete_ids", [])
        delete_ids.append({"chat_id": message.chat.id, "message_id": error_msg.message_id})
        await state.update_data(delete_ids=delete_ids)
    await asyncio.sleep(3)
    data = await state.get_data()
    delete_ids = data.get("delete_ids", [])
    for entry in delete_ids:
        try:
            await message.bot.delete_message(entry["chat_id"], entry["message_id"])
        except Exception:
            pass
    await state.clear()
