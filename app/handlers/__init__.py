"""Handlers package"""
from aiogram import Dispatcher, Router
from app.filters import IsAdmin
from . import admin, user


def setup(dp: Dispatcher) -> None:
    """
    Setup all the handlers and routers, bind filters

    :param Dispatcher dp: Dispatcher (root Router)
    """

    admin_router = Router()
    admin_router.message.filter(IsAdmin())
    admin_router.callback_query.filter(IsAdmin())
    dp.include_router(admin_router)
    admin.setup(admin_router)

    user_router = Router()
    dp.include_router(user_router)
    user.setup(dp, user_router)
