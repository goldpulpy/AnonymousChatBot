"""Dialogue handlers"""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import Router, Bot, types
from aiogram.filters import Text, Command, StateFilter
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
from sqlalchemy import delete, or_, func, update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from settings import SHOW_CONTACTS_PRICE
from app.filters import InDialogue
from app.templates import texts
from app.templates.keyboards import user as nav
from app.utils.config import BaseSettings
from app.database.models import (
    User, Dialogue, Queue, History, Advert, DialogueHistory
)


async def show_ad(
    bot: Bot, state: FSMContext, session: AsyncSession, user: User
) -> None:
    """Show ad handler"""
    if user.is_vip:
        return

    METHODS = (
        None,
        bot.send_photo,
        bot.send_video,
        bot.send_animation,
        bot.send_audio,
        bot.send_voice,
    )

    current_time = datetime.now()
    state_data = await state.get_data()
    next_check = state_data.get('next_ad_check', datetime.fromtimestamp(0))
    if next_check > current_time:
        return

    confirm = await session.scalar(
        select(History).where(
            History.user_id == user.id,
            History.time > current_time - timedelta(minutes=15),
        )
    )

    if confirm:
        return await state.update_data(
            next_ad_check=confirm.time + timedelta(minutes=15),
        )

    ad = await session.scalar(
        select(Advert)
        .where(
            Advert.is_active,
            or_(
                Advert.target == 0,
                Advert.views < Advert.target,
            ),
            Advert.id.notin_(
                select(History.ad_id)
                .where(History.user_id == user.id)
            ),
        )
        .order_by(func.random())
    )

    if not ad:
        return

    if ad.type == 0:
        await bot.send_message(
            user.id,
            ad.text,
            reply_markup=(
                json.loads(ad.markup)
                if ad.markup else None
            ),
            disable_web_page_preview=True,
            disable_notification=True,
        )

    else:
        await METHODS[ad.type](
            user.id,
            ad.file_id,
            caption=ad.text,
            reply_markup=(
                json.loads(ad.markup)
                if ad.markup else None
            ),
            disable_notification=True,
        )

    session.add(
        History(
            user_id=user.id,
            ad_id=ad.id,
        ),
    )
    ad.views += 1

    await session.commit()
    await state.update_data(
        next_ad_check=current_time + timedelta(minutes=15),
    )


async def queue(
    bot: Bot, session: AsyncSession, user: User, state: FSMContext,
    target_man: Optional[bool] = None, is_adult: bool = False
) -> None:
    """Queue handler"""
    stmt = select(Queue) \
        .where(Queue.id != user.id) \
        .where(Queue.is_adult == is_adult) \
        .where(
            or_(
                Queue.target_man == user.is_man,
                Queue.target_man == None,
            ),
    )

    if target_man is not None:
        stmt = stmt.where(Queue.is_man == target_man)

    await state.update_data(
        is_adult=is_adult,
        target_man=target_man,
    )
    match = await session.scalar(stmt)

    if match:
        return await create_dialogue(bot, session, user.id, match.id)

    await session.execute(
        delete(Queue)
        .where(Queue.id == user.id)
    )
    session.add(
        Queue(
            id=user.id,
            is_man=user.is_man,
            target_man=target_man,
            is_adult=is_adult,
        )
    )
    await session.commit()
    await bot.send_message(
        user.id,
        texts.user.DIALOGUE_SEARCH,
    )


async def get_dialogue_id(session: AsyncSession) -> int:
    """Get dialogue id"""
    dialogue_id = await session.scalar(
        select(func.max(DialogueHistory.dialogue_id))
    )
    if dialogue_id is None:
        return 1

    return dialogue_id + 1


async def create_dialogue(
    bot: Bot, session: AsyncSession, first: int, second: int, 
    friend: bool = False
) -> None:
    """Create dialogue"""

    for user_id in (first, second):
        with suppress(TelegramAPIError):
            if friend:
                await bot.send_message(
                    user_id,
                    texts.user.DIALOGUE_FRIEND,
                    reply_markup=nav.reply.DIALOGUE_FRIEND_MENU,
                )

            else:
                await bot.send_message(
                    user_id,
                    texts.user.DIALOGUE_FOUND,
                    reply_markup=nav.reply.DIALOGUE_MENU,
                )

    await session.execute(
        delete(Queue)
        .where(Queue.id.in_((first, second)))
    )

    dialogue_id = await get_dialogue_id(session)

    for user_id in (first, second):
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(dialogue_id=dialogue_id)
        )

    session.add(
        Dialogue(
            first=first,
            second=second,
        )
    )
    await session.commit()


async def delete_dialogue(session: AsyncSession, user_id: int) -> None:

    await session.execute(
        delete(Dialogue)
        .where(
            or_(
                Dialogue.first == user_id,
                Dialogue.second == user_id,
            ),
        )
    )
    await session.commit()


async def finish_dialogue(
    message: types.Message, bot: Bot, state: FSMContext,
    session: AsyncSession, user: User
) -> None:
    """Finish dialogue"""
    await message.answer(
        texts.user.DIALOGUE_END if user.partner else texts.user.SEARCH_END,
        reply_markup=nav.reply.main_menu(user),
    )
    await show_ad(bot, state, session, user)

    await session.execute(
        delete(Queue)
        .where(Queue.id == user.id)
    )

    if not user.partner:
        return await session.commit()

    second_user = await session.get(User, user.partner_id)
    await delete_dialogue(session, user.id)
    user.dialogue_id = None
    second_user.dialogue_id = None
    await session.commit()

    if not second_user:
        return

    with suppress(TelegramAPIError):
        await bot.send_message(
            second_user.id,
            texts.user.DIALOGUE_END,
            reply_markup=nav.reply.main_menu(second_user),
        )

    await show_ad(bot, state, session, second_user)


async def add_friend_request(
    message: types.Message, bot: Bot, session: AsyncSession, user: User
) -> None:
    """Add friend request"""

    if not user.partner:
        return await session.commit()

    second_user = await session.get(User, user.partner_id)
    if not second_user:
        await message.answer('Диалог уже завершен.')
        return

    if user.is_friend(second_user.id):
        return await message.answer(
            '%s уже у вас в друзьях.' % second_user.first_name,
        )

    await message.answer(
        texts.user.ADD_FRIEND_REQUEST,
    )

    with suppress(TelegramAPIError):
        await bot.send_message(
            second_user.id,
            texts.user.ADD_FRIEND_REQUEST_SECOND,
            reply_markup=nav.inline.FRIEND_REQUEST,
        )


async def accept_friend_request(
    call: types.CallbackQuery, bot: Bot, session: AsyncSession, user: User
) -> None:
    """Accept friend request"""
    if not user.partner:
        await call.message.edit_text('Диалог уже завершен.')
        return await session.commit()

    second_user = await session.get(User, user.partner_id)
    if not second_user:
        await call.message.edit_text('Диалог уже завершен.')
        return

    if user.is_friend(second_user.id):
        return await call.message.edit_text(
            '%s уже у вас в друзьях.' % second_user.first_name,
        )

    user.add_friend(second_user.id)
    second_user.add_friend(user.id)
    await session.commit()

    await call.message.edit_text(
        '👥 Запрос в друзья принят, ваш новый друг %s' % second_user.first_name,
    )

    with suppress(TelegramAPIError):
        await bot.send_message(
            second_user.id,
            '👥 Пользователь принял запрос в друзья, ваш новый друг %s'
            % user.first_name,
        )


async def decline_friend_request(
    call: types.CallbackQuery, bot: Bot, session: AsyncSession, user: User
) -> None:
    """Decline friend request"""
    if not user.partner:
        await call.message.edit_text('Диалог уже завершен.')
        return await session.commit()

    second_user = await session.get(User, user.partner_id)

    if not second_user:
        await call.message.edit_text('Диалог уже завершен.')
        return

    await call.message.edit_text('👥 Запрос в друзья отклонен.')

    with suppress(TelegramAPIError):
        await bot.send_message(
            second_user.id,
            '👥 Пользователь отклонил запрос в друзья.',
        )


async def pre_complaint(
    message: types.Message, user: User, state: FSMContext
) -> None:
    """Pre complaint"""
    await message.answer(
        texts.user.PRE_COMPLAINT,
    )
    await state.set_state('dialogue.complaint')


async def view_complaint(
    message: types.Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    """View complaint"""
    await state.clear()

    if not user.partner:
        return await message.answer('Диалог уже завершен.')

    second_user = await session.get(User, user.partner_id)

    if not second_user:
        await message.answer('Диалог уже завершен.')
        return

    await message.answer(
        texts.user.VIEW_COMPLAINT % (message.text),
        reply_markup=nav.inline.COMPLAINT,
    )


async def complaint(
    call: types.CallbackQuery, bot: Bot, session: AsyncSession,
    user: User, config: BaseSettings
) -> None:
    """Complaint"""

    if not user.partner:
        return await call.message.edit_text('Диалог уже завершен.')

    second_user = await session.get(User, user.partner_id)

    if not second_user:
        await call.message.edit_text('Диалог уже завершен.')
        return

    await call.message.edit_text('❗️ Жалоба отправлена.')

    for moder in config.bot.moders:
        with suppress(TelegramAPIError):
            await bot.send_message(
                moder,
                texts.user.COMPLAINT % (
                    user.dialogue_id,
                    hlink(str(user.id), 'tg://user?id=' + str(user.id)),
                    hlink(
                        str(second_user.id),
                        'tg://user?id=' + str(second_user.id)
                    ),
                    call.message.text.split('Причина: ')[-1],
                ),
            )


async def decline_complaint(
    call: types.CallbackQuery, bot: Bot, session: AsyncSession, user: User
) -> None:
    """Decline complaint"""
    if not user.partner:
        await call.message.edit_text('Диалог уже завершен.')
        return await session.commit()

    second_user = await session.get(User, user.partner_id)

    if not second_user:
        await call.message.edit_text('Диалог уже завершен.')
        return

    await call.message.edit_text('❗️ Жалоба отменена.')


async def pre_show_contacts(message: types.Message, user: User) -> None:
    """Pre show contacts"""
    await message.answer(
        texts.user.PRE_SHOW_CONTACTS % (
            int(SHOW_CONTACTS_PRICE),
            user.balance),
        reply_markup=nav.inline.SHOW_CONTACTS,
    )


async def show_contacts(
    call: types.CallbackQuery, bot: Bot, user: User, session: AsyncSession
) -> None:
    """Show contacts"""
    user.balance -= SHOW_CONTACTS_PRICE
    if user.balance < 0:
        return await call.message.edit_text(
            'Недостаточно средств. Пополните баланс.',
        )

    if not user.partner:
        return await call.message.edit_text('Диалог уже завершен.')

    second_user = await session.get(User, user.partner_id)

    if not second_user:
        return await call.message.edit_text(
            'Пользователь не найден. Попробуйте позже.'
        )

    await session.commit()
    await call.message.edit_text(
        texts.user.SHOW_CONTACTS % (
            second_user.first_name,
            '-' if second_user.last_name is None else second_user.last_name,
            'Ссылка' if second_user.username else 'ID',
            '@' + second_user.username if second_user.username
            else hlink(
                str(second_user.id), 'tg://user?id=' + str(second_user.id)
            ),

        )
    )


async def forward_message(
    message: types.Message, bot: Bot, session: AsyncSession, user: User
) -> None:
    """Forward message"""
    try:
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
                file = await bot.get_file(file_id)

                destination = Path(
                    "photo", f"{user.id}_{file.file_unique_id}.jpg"
                )
                await bot.download_file(file.file_path, destination)
                image_id = f"{user.id}_{file.file_unique_id}"

            else:
                image_id = None

            session.add(
                DialogueHistory(
                    dialogue_id=user.dialogue_id,
                    first=user.id,
                    second=user.partner_id,
                    message=message.text if message.text else message.caption,
                    image_id=image_id
                )
            )

            await session.commit()

        except Exception:
            pass

        await message.copy_to(user.partner_id)

    except TelegramBadRequest:
        await message.answer(
            'Ваш собеседник заблокировал бота, диалог окончен!',
        )
        await delete_dialogue(session, user.id)


async def random_normal(
    _, bot: Bot, state: FSMContext, session: AsyncSession, user: User
) -> None:
    """Random normal"""
    await queue(bot, session, user, state=state)


async def male_normal(
    _, bot: Bot, state: FSMContext, session: AsyncSession, user: User
) -> None:
    """Male normal"""
    await queue(bot, session, user, target_man=True, state=state)


async def female_normal(
    _, bot: Bot, state: FSMContext, session: AsyncSession, user: User
) -> None:
    """Female normal"""
    await queue(bot, session, user, target_man=False, state=state)


async def pre_adult(message: types.Message) -> None:
    """Pre adult"""
    await message.answer(
        texts.user.DIALOGUE_GENDER,
        reply_markup=nav.inline.ADULT_GENDER,
    )


async def adult(
    call: types.CallbackQuery, bot: Bot, state: FSMContext,
    session: AsyncSession, user: User
) -> None:
    """Adult"""
    target = call.data.split(':')[1]
    await call.message.delete()
    await queue(
        bot, session, user, target_man=target == 'male',
        is_adult=True, state=state,
    )


async def next(
    message: types.Message, bot: Bot, state: FSMContext,
    session: AsyncSession, user: User
) -> None:
    """Next"""
    if user.partner:
        await finish_dialogue(message, bot, state, session, user)

    state_data = await state.get_data()
    await queue(
        bot, session, user, state=state,
        target_man=state_data.get('target_man'),
        is_adult=state_data.get('is_adult', False),
    )


def register(router: Router) -> None:
    """Register handlers"""
    router.message.register(random_normal, Text('Случайный диалог 🔍'))
    router.message.register(male_normal, Text('Поиск М 👨'))
    router.message.register(female_normal, Text('Поиск Ж 👩'))
    router.message.register(pre_adult, Text('Пошлый чат 🔞'))
    router.callback_query.register(adult, Text(startswith='adult:'))
    router.message.register(next, Command('next'))
    router.message.register(finish_dialogue, Command('stop'))
    router.message.register(finish_dialogue, Text('Завершить диалог 🚫'))
    router.message.register(add_friend_request, Text('Добавить в друзья 👥'))
    router.callback_query.register(
        accept_friend_request, Text('accept:friend')
    )
    router.callback_query.register(
        decline_friend_request, Text('decline:friend')
    )
    router.message.register(pre_show_contacts, Text('Показать контакты 📱'))
    router.callback_query.register(show_contacts, Text('show:contacts'))
    router.message.register(pre_complaint, Text('Пожаловаться 💬'))
    router.message.register(view_complaint, StateFilter('dialogue.complaint'))
    router.callback_query.register(complaint, Text('accept:complaint'))
    router.callback_query.register(
        decline_complaint, Text('decline:complaint')
    )
    router.message.register(forward_message, InDialogue())
