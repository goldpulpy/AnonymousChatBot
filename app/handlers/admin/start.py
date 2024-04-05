from app.templates.keyboards import admin as nav

from aiogram import Router, types
from aiogram.filters import CommandStart


async def start(message: types.Message):

    await message.answer(
        'Админ-панель',
        reply_markup=nav.reply.MENU,
    )



def register(router: Router):

    router.message.register(start, CommandStart())


