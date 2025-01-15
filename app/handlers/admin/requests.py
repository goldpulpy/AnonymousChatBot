"""Requests handlers"""
from aiogram import Router, types
from aiogram.filters import Command, Text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.templates.keyboards import admin as nav
from app.database.models import RequestChannel


async def get_channels(session: AsyncSession) -> list[RequestChannel]:
    """Get channels handler"""
    channels = await session.scalars(
        select(RequestChannel)
    )
    return channels.all()


async def menu(message: types.Message, session: AsyncSession) -> None:
    """Menu handler"""
    await message.answer(
        'Список каналов с заявками',
        reply_markup=nav.inline.channels(
            await get_channels(session),
        )
    )


async def channels(
    call: types.CallbackQuery, session: AsyncSession,
) -> None:
    """Channels handler"""
    await call.message.edit_text(
        'Список каналов с заявками',
        reply_markup=nav.inline.channels(
            await get_channels(session),
        )
    )


async def channel(
    call: types.CallbackQuery, session: AsyncSession,
) -> None:
    """Channel handler"""
    action, channel_id = call.data.split(':')[1:]

    if action == 'list':
        return await channels(call, session)

    if action == 'del':
        return await call.message.edit_text(
            'Вы уверены, что хотите удалить канал?',
            reply_markup=nav.inline.choice(channel_id, 'request'),
        )

    channel = await session.scalar(
        select(RequestChannel)
        .where(RequestChannel.id == int(channel_id))
    )

    if action == 'del2':
        await session.delete(channel)

    elif action == 'active':
        channel.active = not channel.active

    await session.commit()
    await channels(call, session)


def register(router: Router) -> None:
    """Register requests handlers"""
    router.message.register(menu, Command("requests"))
    router.message.register(menu, Text("Заявки"))
    router.callback_query.register(channel, Text(startswith="request:"))
