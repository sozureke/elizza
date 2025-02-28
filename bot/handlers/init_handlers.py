from .auth import auth_router
from aiogram import Dispatcher

def register_handlers(dp: Dispatcher) -> None:
	dp.include_router(auth_router)