from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def auth_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔑 Authorize")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 My grades")],
            [KeyboardButton(text="🚪 Log out")]
        ],
        resize_keyboard=True
    )

def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )