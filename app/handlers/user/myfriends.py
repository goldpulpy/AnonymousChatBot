"""My friends handlers"""
from aiogram import Router, types, Bot
from aiogram.filters import Text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from app.templates import texts
from app.templates.keyboards import user as nav
from app.database.models import User, Dialogue
from app.handlers.user.dialogue import create_dialogue


async def get_friend_list(session: AsyncSession, user: User) -> list:
    """Get friend list"""
    friends: list = []
    for friend_id in user.friends_list:
        friend = await session.get(User, friend_id)
        if friend:
            status = '🔴' if friend.block_date else '🟢'

            if not friend.block_date:
                in_dialogue = await session.scalar(
                    select(Dialogue).where(
                        or_(
                            Dialogue.second == friend.id,
                            Dialogue.first == friend.id,
                        )
                    )
                )
                if in_dialogue:
                    status = '🟡'

            friends.append({
                'status': status,
                'user': friend,
            })
    return friends


async def friends_list(
    message: types.Message, session: AsyncSession, user: User
) -> None:
    """Friends list handler"""
    friends = await get_friend_list(session, user)
    await message.answer(
        texts.user.MY_FRIENDS % len(user.friends_list),
        reply_markup=nav.inline.friends(friends),
    )


async def back_to_friends(
    call: types.CallbackQuery, session: AsyncSession, user: User
) -> None:
    """Back to friends handler"""
    friends = await get_friend_list(session, user)
    await call.message.edit_text(
        texts.user.MY_FRIENDS % len(user.friends_list),
        reply_markup=nav.inline.friends(friends),
    )


async def get_friend_status(
    friend: User, session: AsyncSession
) -> int:
    """Get friend status"""
    status = 3 if friend.block_date else 1

    if not friend.block_date:
        in_dialogue = await session.scalar(
            select(Dialogue).where(
                or_(
                    Dialogue.second == friend.id,
                    Dialogue.first == friend.id,
                )
            )
        )
        if in_dialogue:
            status = 2

    return status


async def get_friend(
    call: types.CallbackQuery, session: AsyncSession
) -> None:
    """Get friend handler"""
    friend_id = int(call.data.split(':')[-1])
    friend = await session.get(User, friend_id)

    if not friend:
        await call.answer(
            'Друг с таким id не найден в базе.', show_alert=True
        )
        return await call.message.delete()

    status = {
        1: '🟢',
        2: '🟡',
        3: '🔴',
    }

    friend_status = await get_friend_status(friend, session)
    await call.message.edit_text(
        texts.user.FRIEND_INFO % (
            status[friend_status],
            friend.first_name,
            ('Мужской' if friend.is_man else 'Женский'),
            friend.age,
            ('есть' if friend.is_vip else 'нет'),
        ),
        reply_markup=nav.inline.friend(friend.id),
    )


async def friend_dialogue_request(
    call: types.CallbackQuery, bot: Bot, session: AsyncSession, user: User
) -> None:
    """Friend dialogue request handler"""
    friend_id = int(call.data.split(':')[-1])
    friend = await session.get(User, friend_id)

    if not friend:
        await call.answer(
            'Друг с таким id не найден в базе.', show_alert=True
        )

        return await call.message.delete()

    friend_status = await get_friend_status(friend, session)
    if friend_status == 3:
        await call.answer(
            'Ваш друг заблокировал бота, невозможно запросить диалог.',
            show_alert=True
        )

    elif friend_status == 2:
        await call.answer(
            'Ваш друг уже в диалоге, невозможно запросить диалог.',
            show_alert=True
        )

    else:
        await call.message.edit_text(
            '💬 Запрос на диалог отправлен другу %s' % friend.first_name,
        )

        await bot.send_message(
            friend.id,
            texts.user.FRIEND_DIALOGUE_REQUEST % (
                user.first_name,
            ),
            reply_markup=nav.inline.friend_dialogue_request(user.id),
        )


async def decline_dialogue_request(
    call: types.CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    user: User
) -> None:
    """Decline dialogue request handler"""
    friend_id = int(call.data.split(':')[-1])
    friend = await session.get(User, friend_id)

    if not friend:
        await call.answer(
            'Друг с таким id не найден в базе.',
            show_alert=True
        )
        return await call.message.delete()

    await call.message.edit_text(
        '💬 Запрос на диалог отклонен',
    )
    await bot.send_message(
        friend.id,
        '❌ Ваш друг %s отклонил приглашение на диалог' % user.first_name,
    )


async def accept_dialogue_request(
    call: types.CallbackQuery,
    bot: Bot,
    session: AsyncSession,
    user: User
) -> None:
    """Accept dialogue request handler"""
    friend_id = int(call.data.split(':')[-1])
    friend = await session.get(User, friend_id)

    if not friend:
        await call.answer(
            'Друг с таким id не найден в базе.', show_alert=True
        )

        return await call.message.delete()

    friend_status = await get_friend_status(friend, session)
    if friend_status == 3:
        await call.message.edit_text(
            '❌ Ваш друг заблокировал бота, невозможно принять диалог.',
        )

    elif friend_status == 2:
        await call.message.edit_text(
            '❌ Ваш друг уже в диалоге, невозможно принять диалог.',
        )

    else:
        await call.message.edit_text(
            '💬 Запрос на диалог с %s принят' % friend.first_name,
        )

        await bot.send_message(
            friend.id,
            '✅ Ваш друг %s принял приглашение на диалог' % user.first_name,
        )

        await create_dialogue(
            bot,
            session,
            user.id, friend.id,
            friend=True
        )


def register(router: Router) -> None:
    """Register handlers"""
    router.message.register(friends_list, Text('Мои друзья 👥'))
    router.callback_query.register(get_friend, Text(startswith="friend:get"))
    router.callback_query.register(
        friend_dialogue_request, Text(startswith='friend:dialogue')
    )
    router.callback_query.register(back_to_friends, Text("friend:back"))
    router.callback_query.register(
        accept_dialogue_request, Text(startswith='accept:dialogue:friend')
    )
    router.callback_query.register(
        decline_dialogue_request, Text(startswith='decline:dialogue:friend')
    )
