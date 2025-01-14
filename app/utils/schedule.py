"""Schedule utils"""
import asyncio
import logging
from datetime import datetime
from contextlib import suppress
from typing import NoReturn

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database.models import Request

logger = logging.getLogger('joinrequest')


class JoinRequestChecker(object):
    def __init__(self, bot: Bot, sessionmaker: async_sessionmaker) -> None:
        """
        Initialize the JoinRequestChecker class

        :param Bot bot: Aiogram bot instance
        :param async_sessionmaker sessionmaker: Async sessionmaker
        """

        self.bot = bot
        self.sessionmaker = sessionmaker

    async def approve(self) -> None:
        """Approve join requests"""
        async with self.sessionmaker() as session:
            requests = await session.scalars(
                select(Request)
                .where(Request.time < datetime.now())
            )
            requests = requests.all()

            for request in requests:
                await self.safe_approve(request)

            request_ids = [
                request.id
                for request
                in requests
            ]

            await session.execute(
                delete(Request)
                .where(Request.id.in_(request_ids))
            )
            await session.commit()

    async def checker(self) -> NoReturn:
        """Check join requests"""
        logger.info('Strated checking join requests')
        while True:
            await self.approve()
            await asyncio.sleep(15)

    async def safe_approve(self, request: Request) -> None:
        """Safe approve join request"""
        with suppress(TelegramAPIError):
            await self.bot.approve_chat_join_request(
                chat_id=request.chat_id,
                user_id=request.user_id,
            )


async def setup(bot: Bot, sessionmaker: async_sessionmaker) -> None:
    """
    Start polling the database for JoinRequests

    :param Bot bot: Aiogram bot instance
    :param async_sessionmaker sessionmaker: Async sessionmaker
    """

    joinrequest = JoinRequestChecker(bot, sessionmaker)
    asyncio.create_task(joinrequest.checker())
