import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers.init_handlers import register_handlers
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

load_dotenv(dotenv_path=".env.local")

bot = Bot(
    token=os.getenv("TELEGRAM_BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode="HTML") 
)
dp = Dispatcher(storage=MemoryStorage())
register_handlers(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


