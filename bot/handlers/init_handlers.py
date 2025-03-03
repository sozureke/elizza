from .auth import auth_router
from .course import course_router
from .assignment import  assignments_router
from .grade import grades_router
from .communication import communication_router
from aiogram import Dispatcher

def register_handlers(dp: Dispatcher) -> None:
	dp.include_router(communication_router)
	dp.include_router(auth_router)
	dp.include_router(course_router)
	dp.include_router(assignments_router)
	dp.include_router(grades_router)