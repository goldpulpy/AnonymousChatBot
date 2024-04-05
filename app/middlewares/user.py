from app.database.models import User, Referral
from app.utils.text import get_ref

from typing import Any, Awaitable, Callable, Dict, Optional
from contextlib import suppress

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import Update
from aiogram.exceptions import TelegramAPIError

from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserMiddleware(BaseMiddleware):
    """
    Middleware for registering user.
    """


    @staticmethod
    async def user_ref(link: str, bot: Bot, session: AsyncSession):

        referral = await session.scalar(
            select(User)
            .where(User.id == int(link))
        )

        if not referral: 

            return

        referral.invited += 1

        if referral.invited % 5 != 0:

            return

        referral.add_vip(1)

        with suppress(TelegramAPIError):

            await bot.send_message(
                referral.id,
                '<i><b>По вашей ссылке перешло 5 человек. Вам начислена VIP-подписка 🥰</></>',
            )


    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:


        event_user: Optional[types.User] = data.get("event_from_user")
        event_chat: Optional[types.Chat] = data.get("event_chat")


        if not event_user or event.chat_join_request:

            return await handler(event, data)

        session: AsyncSession = data['session']



        user = await session.scalar(
            select(User)
            .where(User.id == event_user.id)
            .options(selectinload(User.partner))
        )

        if user:
            user.username = event_user.username
            user.first_name = event_user.first_name
            user.last_name = event_user.last_name
            await session.commit()

        if not user and not event.inline_query:

            ref = None
            
            if getattr(event.message, 'text', False):

                link = get_ref(event.message)

                if link and link.isdigit():

                    await self.user_ref(link, data['bot'], session)

                else:
                
                    referral = await session.scalar(
                        select(Referral)
                        .where(Referral.ref == link)
                    )

                    if referral:

                        ref = referral.ref

            user = User(
                id=event_user.id,
                ref=ref,
                chat_only=getattr(event_chat, 'type', None) != 'private',
            )
            session.add(user)
            
            await session.commit()
            await session.refresh(user, ['partner'])

        elif getattr(event_chat, 'type', None) == 'private' and user.chat_only:

            user.chat_only = False
            await session.commit()

        data["user"] = user

        return await handler(event, data)
