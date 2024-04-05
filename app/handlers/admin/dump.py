from app.templates.keyboards import admin as nav
from app.database.models import User

from io import BytesIO
from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command, Text

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_users(call: types.CallbackQuery, session: AsyncSession, select_alive: bool=False, select_vip: bool=False):

    stmt = select(User.id).where(User.chat_only == False)
    
    if select_alive:

        stmt = stmt.where(User.block_date == None)

    if select_vip:

        stmt = stmt.where(User.vip_time < datetime.now())

    users = (await session.scalars(stmt)).all()

    file = BytesIO()
    file.writelines(
        '%i\n'.encode() % user 
        for user in users
    )
    file.seek(0)

    await call.message.answer_document(
        types.BufferedInputFile(file.read(), 'users.txt'),
        caption=f"Выгружено пользователей: {len(users)}",
    )
    await call.message.delete()


async def dump_users(call: types.CallbackQuery, session: AsyncSession):

    action = call.data.split(":")[1]
    await get_users(
        call, 
        session,
        select_alive=(action != "dead"),
        select_vip=(action == "vip"),
    )


async def pre_dump_users(message: types.Message):

    await message.answer(
        "Каких пользователей выгрузить?",
        reply_markup=nav.inline.DUMP,
    )


def register(router: Router):

    router.message.register(pre_dump_users, Command("dump"))
    router.message.register(pre_dump_users, Text("Выгрузка"))

    router.callback_query.register(dump_users, Text(startswith="dump"))
