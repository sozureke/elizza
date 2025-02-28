from .auth import auth_router
from .courses import course_router
from .assignment import  assignments_router
from aiogram import Dispatcher

def register_handlers(dp: Dispatcher) -> None:
	dp.include_router(auth_router)
	dp.include_router(course_router)
	dp.include_router(assignments_router)