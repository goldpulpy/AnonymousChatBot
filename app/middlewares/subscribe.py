import time
import aiohttp
import asyncio

from app.utils.config import Settings
from app.database.models import User, Sponsor

from functools import lru_cache
from contextlib import suppress
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, Chat
from aiogram.exceptions import (
    TelegramNotFound,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramAPIError,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.token import TokenValidationError

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

class SubMiddleware(BaseMiddleware):
    """
    Middleware for checking user's subscription
    """

    def __init__(self):

        self.session = aiohttp.ClientSession()


    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:

        user: Optional[User] = data.get('user')
        config: Settings = data['config']
        state: FSMContext = data['state']
        session: AsyncSession = data['session']
        chat: Optional[Chat] = data.get('event_chat')

        data["sponsors"] = []

        if not chat or getattr(user, 'id', 0) in config.bot.admins or user.is_admin:
            return await handler(event, data)

        state_data = await state.get_data()


        if chat.type != 'private' or user.is_vip:
            
            return await handler(event, data)

        user = user or data.get('event_from_user')

        sponsors = await session.scalars(
            select(Sponsor)
            .where(Sponsor.is_active == True)
        )
        sponsors = sponsors.all()


        available_sponsors = await self.get_sponsors(sponsors, user, data['bot'])
        data['sponsors'] = available_sponsors


        return await handler(event, data)


    async def get_sponsors(self, sponsors: list[Sponsor], user: User, bot: Bot) -> list[Sponsor]:

        response = await asyncio.gather(
            *(
                self._check_sub(sponsor, user, bot)
                for sponsor in [
                    obj for obj in sponsors
                    if obj.check
                ]
            ),
        )
        not_subbed = [
            sponsor for sponsor in response
            if sponsor is not None
        ]

        if bool(not_subbed):

            return not_subbed + [
                sponsor for sponsor in sponsors 
                if not sponsor.check
            ]

        return []


    async def _check_sub(self, sponsor: Sponsor, user: User, bot: Bot) -> Optional[Sponsor]:
        if sponsor.is_bot:
            
            try:

                bot_ = Bot(sponsor.access_id, session=bot.session)
                await bot_.send_chat_action(user.id, 'typing')

            except TokenValidationError:

                with suppress(ValueError):

                    self._validate_botstat_token(sponsor.access_id)

                    async with self.session.get(
                        'https://api.botstat.io/checksub/%s/%i' % (
                            sponsor.access_id, user.id,
                        )
                    ) as response:

                        data = await response.json(content_type=None)

                        if not data['ok']:

                            return sponsor

            except (
                TelegramNotFound,
                TelegramBadRequest,
                TelegramForbiddenError,
            ):
            
                return sponsor

        else:

            with suppress(TelegramAPIError):

                member = await bot.get_chat_member(
                    sponsor.access_id,
                    user.id,
                )

                if member.status in ('left', 'kicked', None):
                    return sponsor


    @staticmethod
    @lru_cache
    def _validate_botstat_token(token: str):

        if len(token.split('-')) != 5:

            raise ValueError
