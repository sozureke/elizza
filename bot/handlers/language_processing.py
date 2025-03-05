import asyncio
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.main_menu import main_menu_keyboard
from utils.language_processing import NLPProcessor
from utils.delete import deletion_helper

language_processing_router = Router()
nlp_processor = NLPProcessor()


class ChatState(StatesGroup):
    active = State()

def chat_mode_keyboard() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔙 Back to menu")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

@language_processing_router.message(lambda msg: msg.text == "📩 Сhat with me")
async def start_chat_mode(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)

    instructions = (
        "📝 *Chat mode activated!*\n\n"
        "You can now ask me about:\n"
        "• Your Moodle courses (grades, assignments, etc.)\n"
        "• Today's date\n"
        "• Weather\n"
        "• Jokes\n"
        "• Or just say 'hello', 'how are you', etc.\n\n"
        "To exit, press 🔙 *Back to menu*."
    )

    msg = await message.answer(
        instructions,
        reply_markup=chat_mode_keyboard(),
        parse_mode="Markdown"
    )
    deletion_helper.record_message(message.chat.id, msg.message_id)

    await state.set_state(ChatState.active)

@language_processing_router.message(lambda msg: msg.text == "🔙 Back to menu")
async def exit_chat_mode(message: types.Message, state: FSMContext):
    deletion_helper.record_message(message.chat.id, message.message_id)

    msg = await message.answer("Returning to main menu...", reply_markup=main_menu_keyboard())
    deletion_helper.record_message(message.chat.id, msg.message_id)

    await state.clear()

@language_processing_router.message(ChatState.active)
async def handle_text_message(message: types.Message):
    
    deletion_helper.record_message(message.chat.id, message.message_id)

    
    response = nlp_processor.process_message(message.text)

    
    if isinstance(response, dict):
        text = response.get("text", "No text provided.")
        markup = response.get("reply_markup", None)
        msg = await message.answer(text=text, reply_markup=markup)
    else:
        
        msg = await message.answer(text=response)

    deletion_helper.record_message(message.chat.id, msg.message_id)
