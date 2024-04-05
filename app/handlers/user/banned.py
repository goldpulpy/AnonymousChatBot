from app.filters import IsBanned

from app.templates import texts
from app.database.models import User
from aiogram import Router, types

from sqlalchemy.ext.asyncio import AsyncSession



async def user_banned(message: types.Message, session: AsyncSession, user: User):

    await message.answer(
        texts.user.BANNED,
    )






def register(router: Router):

    router.message.register(user_banned, IsBanned(True))