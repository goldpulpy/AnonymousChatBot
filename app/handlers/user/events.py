import random

from app.templates.keyboards import user as nav
from app.database.models import User, Request, RequestChannel

from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Text
from aiogram.exceptions import TelegramAPIError

from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


EMOJIS = ['🛥️', '🛩️', '🏎️', '⏳', '👾', '🌐']

async def my_chat_member(update: types.ChatMemberUpdated, session: AsyncSession, user: User):

    if update.chat.type == 'channel':

        return

    if update.chat.type != 'private':

        if update.new_chat_member.status in ('left', 'kicked'):

            await session.execute(
                delete(User)
                .where(User.id == update.chat.id)
            )

        elif not await session.get(User, update.chat.id):
            
            session.add(
                User(id=update.chat.id)
            )
    else:
        
        if update.new_chat_member.status in ("left", "kicked"):

            user.block_date = datetime.now()

        elif user.block_date:

            user.block_date = None
    
    await session.commit()


async def chat_join_request(update: types.ChatJoinRequest, bot: Bot, session: AsyncSession):

    channel = await session.scalar(
        select(RequestChannel)
        .where(RequestChannel.id == update.chat.id)
    )
    
    if not channel:
        
        channel = RequestChannel(
            id=update.chat.id,
            title=update.chat.title or str(update.chat.id),
        )
        session.add(channel)
        return await session.commit()

    if not channel.active:

        return

    channel.visits += 1
    emoji = random.choice(EMOJIS)

    try:

        await bot.send_message(
            update.from_user.id,
            '❌ <b>Ваши действия похожи на робота.</b>\nДля принятия заявки пройдите проверку.\n❗<i>Выберите %s на клавиатуре ниже</i>' % emoji,
            reply_markup=nav.reply.JOIN_REQUEST,
        )

    except TelegramAPIError:

        return await update.approve()

    session.add(
        Request(
            user_id=update.from_user.id,
            chat_id=update.chat.id,
            time=datetime.now() + timedelta(minutes=5),
        )
    )
    await session.commit()


async def safe_approve(bot: Bot, request: Request, session: AsyncSession):

    with suppress(TelegramAPIError):

        await bot.approve_chat_join_request(
            chat_id=request.chat_id,
            user_id=request.user_id,
        )

    await session.execute(
        delete(Request)
        .where(Request.id == request.id)
    )


async def captcha(message: types.Message, bot: Bot, session: AsyncSession, user: User):

    await message.answer(
        'Ваша заявка принята ✅',
        reply_markup=nav.reply.main_menu(user),
    )

    requests = await session.scalars(
        select(Request)
        .where(Request.user_id == message.from_user.id)
    )

    for request in requests.all():

        await safe_approve(bot, request, session)

    await session.commit()


def register(dp: Dispatcher):

    dp.my_chat_member.register(my_chat_member)
    dp.chat_join_request.register(chat_join_request)

    dp.message.register(captcha, Text(EMOJIS))
