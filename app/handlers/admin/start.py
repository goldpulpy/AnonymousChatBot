"""Admin start handlers"""
from aiogram import Router, types
from aiogram.filters import CommandStart

from app.templates.keyboards import admin as nav


async def start(message: types.Message) -> None:
    """Admin start handler"""
    await message.answer('Админ-панель', reply_markup=nav.reply.MENU)


def register(router: Router) -> None:
    """Register admin start handlers"""
    router.message.register(start, CommandStart())
