import asyncio

from app.utils.config import Settings
from app.database.models import User
from app.templates.keyboards import ADMIN_COMMANDS, USER_COMMANDS

from typing import Optional
from contextlib import suppress

from aiogram import Bot, exceptions
from aiogram.types import BotCommandScopeChat

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def set_commands(
    bot: Bot, 
    config: Settings, 
    sessionmaker: Optional[async_sessionmaker]=None, 
    session: Optional[AsyncSession]=None,
):
    """
    Set bot commands for users and admins.

    :param Bot bot: AIOGram Bot object
    :param Settings config: Settings parsed from .env
    :param async_sessionmaker sessionmaker: Sessionmaker
    """

    await bot.set_my_commands(USER_COMMANDS)

    if sessionmaker:

        session = sessionmaker()

    admin_ids = await session.scalars(
        select(User.id)
        .where(User.is_admin == True)
    )

    if sessionmaker:

        await asyncio.shield(session.close())

    for chat_id in admin_ids.all():

        with suppress(exceptions.TelegramBadRequest):

            await bot.set_my_commands(
                ADMIN_COMMANDS[:-1] + USER_COMMANDS[1:],  # remove /admin and second /start from list
                scope=BotCommandScopeChat(chat_id=chat_id),
            )

    for chat_id in config.bot.admins:

        with suppress(exceptions.TelegramBadRequest):

            await bot.set_my_commands(
                ADMIN_COMMANDS + USER_COMMANDS[1:],  # remove /start
                scope=BotCommandScopeChat(chat_id=chat_id),
            )
