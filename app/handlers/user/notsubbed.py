"""Not subbed handlers"""
from contextlib import suppress

from aiogram import Router, types, exceptions
from aiogram.filters import Text

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.templates import texts
from app.templates.keyboards import user as nav
from app.database.models import User, Sponsor
from app.filters import NotSubbed


async def notsubbed(
    message: types.Message,
    session: AsyncSession,
    user: User,
    sponsors: list[Sponsor]
) -> None:
    """Not subbed handler"""
    await message.answer(
        texts.user.NOT_SUBBED,
        reply_markup=nav.inline.subscription(sponsors),
    )

    if user.subbed:
        user.subbed = False
        await session.commit()


async def notsubbed_cb(
    call: types.CallbackQuery,
    session: AsyncSession,
    user: User,
    sponsors: list[Sponsor]
) -> None:
    """Not subbed callback handler"""

    await call.answer('Вы не подписаны на одного из спонсоров.', True)
    with suppress(exceptions.TelegramAPIError):
        await call.message.edit_text(
            texts.user.NOT_SUBBED,
            reply_markup=nav.inline.subscription(sponsors),
        )

    if user.subbed:
        user.subbed = False
        await session.commit()


async def subbed(
    call: types.CallbackQuery,
    session: AsyncSession,
    user: User
) -> None:
    """Subbed handler"""

    await call.message.delete()
    await call.message.answer(
        texts.user.START,
        reply_markup=nav.reply.main_menu(user),
    )

    if user.subbed_before and user.subbed:
        return

    user.subbed = True
    if not user.subbed_before:
        user.subbed_before = True
        await session.execute(
            update(Sponsor)
            .where(Sponsor.is_active == True)
            .values(visits=Sponsor.visits + 1)
        )
        await session.execute(
            update(Sponsor)
            .where(Sponsor.limit != 0, Sponsor.visits >= Sponsor.limit)
            .values(is_active=False)
        )
    await session.commit()


def register(router: Router) -> None:
    """Register handlers"""
    router.message.register(notsubbed, NotSubbed())
    router.callback_query.register(notsubbed_cb, NotSubbed())
    router.callback_query.register(subbed, Text('checksub'))
