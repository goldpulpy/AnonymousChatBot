from app.templates import texts
from app.templates.keyboards import user as nav
from app.database.models import User, Room
from app.filters import InRoom



from contextlib import suppress

from aiogram import Router, types, Bot
from aiogram.filters import Text, Command, StateFilter, CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from settings import CHANGE_NICKNAME_IN_ROOM_PRICE


async def room_list(message: types.Message, session: AsyncSession):


    rooms = await session.scalars(
        select(Room)
    )


    await message.answer(
        '🏠 Список комнат:',
        reply_markup=nav.inline.room_list(rooms),
    )

async def join_room(call: types.CallbackQuery, 
                    state: FSMContext, 
                    session: AsyncSession, 
                    bot: Bot, user: User):

    room_id = int(call.data.split(':')[-1])

    room: Optional[Room] = await session.scalar(
        select(Room)
        .where(Room.id == room_id)
    )


    if not room:

        return await call.answer(
            'Такой комнаты не существует или она была удалена.',
            show_alert=True
        )

    if user.in_room == room_id:

        return await call.answer(
            'Вы уже уже в данной комнате.',
            show_alert=True
        )

    if user.in_room != 0:

        return await call.answer(
            'Невозможно войти в несколько комнат, пожалуйста, выйдите из текущей комнаты.',
            show_alert=True
        )

    if room.room_online_members >= room.room_online_limit:

        return await call.answer(
            'Комната переполнена.',
            show_alert=True
        )

    user.in_room = room_id

    nickname: str = room.join_room(user.id, user.is_man)

    room.room_online_members += 1

    await session.commit()


    await call.message.delete()

    await bot.send_message(
        user.id,
        texts.user.JOIN_ROOM % (room.room_name, nickname, room.room_online_members),
        reply_markup=nav.reply.ROOM_MENU
    )
    
    online_users: list = room.get_online_members()

    for online_user in online_users:
        
        try:
            await bot.send_message(
                online_user,
                '👋 Пользователь <code>%s</code> вошел в комнату!' % (nickname)
            )
        except:

            pass

async def room_members(message: types.Message, 
                       session: AsyncSession,
                       bot: Bot, user: User):

    if user.in_room == 0:

        return await message.answer(
            'Вы не в комнате.',
        )

    room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    if not room:


        await message.answer(
            'Такой комнаты не существует или она была удалена.',
            reply_markup=nav.reply.main_menu(user),
        )

        user.in_room = 0

        return await session.commit()

    room_members: list = room.get_online_members_nickname()

    await message.answer(
        '👥 <b>Комната %s состоит из:</b> %s' % (room.room_name, ', '.join(room_members)),
    )




async def leave_room(message: types.Message, 
                     session: AsyncSession,
                     bot: Bot, 
                     user: User):


    if user.in_room == 0:

        return await message.answer(
            'Вы не в комнате.',
        )

    room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    user.in_room = 0

    if not room:

        await message.answer(
            'Такой комнаты не существует или она была удалена.',
            reply_markup=nav.reply.main_menu(user),
        )

        return await session.commit()

    room.leave_room(user.id)

    room.room_online_members -= 1

    await session.commit()

    await message.answer(
        'Вы вышли из комнаты %s.' % room.room_name,
        reply_markup=nav.reply.main_menu(user),
    )

    online_users: list = room.get_online_members()
    nickname: str = room.get_nickname(user.id)

    for online_user in online_users:

        try:
            await bot.send_message(
                online_user,
                '👋 Пользователь <code>%s</code> вышел из комнаты!' % (nickname)
            )
        except:

            pass


async def pre_change_nickname(message: types.Message,
                    state: FSMContext, 
                    session: AsyncSession,
                    bot: Bot, user: User):

    room: Room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    nickname: str = room.get_nickname(user.id)

    await message.answer(
        texts.user.PRE_ROOM_CHANGE_NICKNAME % (
            room.room_name,
            nickname,
            int(CHANGE_NICKNAME_IN_ROOM_PRICE),
            user.balance),
        reply_markup=nav.inline.PRE_CHANGE_NICKNAME,
    )

async def change_nickname(call: types.CallbackQuery,
                    state: FSMContext,
                    session: AsyncSession,
                    bot: Bot, user: User):
    
    user.balance -= CHANGE_NICKNAME_IN_ROOM_PRICE

    if user.balance < 0:

        return await call.message.edit_text(
            'Недостаточно средств. Пополните баланс.',
        )
    
    if user.in_room == 0:

        return await call.message.edit_text(
            'Вы не в комнате.',
        )

    await call.message.edit_text(
        '✏️ Напишите новый никнейм.',
    )

    await state.set_state('change.nickname')

async def new_change_nickname(message: types.Message,
                    state: FSMContext,
                    session: AsyncSession,
                    bot: Bot, user: User):

    room: Room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    if not room:

        await message.answer(
            'Такой комнаты не существует или она была удалена.',
            reply_markup=nav.reply.main_menu(user),
        )

        user.in_room = 0

        await session.commit()

        return await state.clear()

    if user.in_room == 0:

        await call.message.edit_text(
            'Вы не в комнате.',
        )

        return await state.clear()

    new_nickname: str = message.text

    if len(new_nickname) > 10:

        return await message.answer(
            'Никнейм не должен превышать 20 символов, повторите попытку.',
        )

    
    if len(new_nickname) < 3:

        return await message.answer(
            'Никнейм должен содержать не менее 3 символов, повторите попытку.',
        )

    nicknames: list = room.get_online_members_nickname()

    old_nickname: str = room.get_nickname(user.id)

    if new_nickname in nicknames:

        return await message.answer(
            'Такой никнейм уже используется, повторите попытку.',
        )

    await state.clear()

    await message.answer(
        texts.user.ROOM_CHANGE_NICKNAME % (
        room.room_name, 
        old_nickname, 
        new_nickname,
        int(CHANGE_NICKNAME_IN_ROOM_PRICE),
        user.balance),
        reply_markup=nav.inline.change_nickname(new_nickname),
    )


async def accept_change_nickname(call: types.CallbackQuery,
                    state: FSMContext,
                    session: AsyncSession,
                    bot: Bot, user: User):

    room: Room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    if not room:

        await call.message.edit_text(
            'Такой комнаты не существует или она была удалена.',
            reply_markup=nav.reply.main_menu(user),
        )

        user.in_room = 0

        return await session.commit()

    if user.in_room == 0:

        return await call.message.edit_text(
            'Вы не в комнате.',
        )

    new_nickname: str = call.data.split(':')[-1]
    old_nickname: str = room.get_nickname(user.id)

    user.balance -= CHANGE_NICKNAME_IN_ROOM_PRICE

    if user.balance < 0:

        return await call.message.edit_text(
            'Недостаточно средств. Пополните баланс.',
        )

    room.change_nickname(user.id, new_nickname)

    await session.commit()


    await call.message.edit_text(
        '🔄 Никнейм успешно изменен на %s.' % new_nickname,
    )

    room_online_members: list = room.get_online_members()

    for member in room_online_members:

        if member != user.id:

            await bot.send_message(
                member,
                '🔄 <code>%s</code> сменил никнейм на <code>%s</code>.' % (old_nickname, new_nickname)
            )

async def decline_change_nickname(call: types.CallbackQuery,
                                  state: FSMContext,
                                  session: AsyncSession,
                                  bot: Bot, user: User):

    room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    if not room:

        await call.message.edit_text(
            'Такой комнаты не существует или она была удалена.',
            reply_markup=nav.reply.main_menu(user),
        )

        user.in_room = 0

        return await session.commit()


    if user.in_room == 0:

        return await call.message.edit_text(
            'Вы не в комнате.',
        )

    await state.clear()

    await call.message.edit_text(
        '🔄 Действие отменено.',
    )


async def chatting(message: types.Message, 
                   state: FSMContext, 
                   session: AsyncSession, 
                   bot: Bot, user: User):


    if user.in_room == 0:

        return await message.answer(
            'Вы не в комнате.',
        )

    room = await session.scalar(
        select(Room)
        .where(Room.id == user.in_room)
    )

    if not room:

        await message.answer(
            '🏠 Комната была удалена.',
            reply_markup=nav.reply.main_menu(user),
        )

        user.in_room = 0

        await session.commit()

        return

    
    online_users: list = room.get_online_members()
    nickname: str = room.get_nickname(user.id)

    for online_user in online_users:

        if online_user != user.id:

            try:

                if message.text is not None:

                    await bot.send_message(
                        online_user,
                        '<b>%s</b>: %s' % (nickname, message.text)
                    )

                else:

                    await bot.send_photo(
                        online_user,
                        message.photo[-1].file_id,
                        caption='<b>%s</b>: %s' % (
                            nickname, message.caption if message.caption else 'Фотография'),
                    )


            except:

                pass






def register(router: Router):


    router.message.register(room_list, Text("Комнаты 🏠"))

    router.message.register(leave_room, Text("Выйти из комнаты 🚪"))
    router.message.register(leave_room, Command('leave'))


    router.message.register(room_members, Command('members'))
    router.message.register(room_members, Text("Участники 👤"))

    router.message.register(pre_change_nickname, Text("Сменить ник в комнате 🔄"))
    router.callback_query.register(change_nickname, Text('change:nickname'))
    router.message.register(new_change_nickname, StateFilter('change.nickname'))
    router.callback_query.register(accept_change_nickname, Text(startswith='accept:change:nickname'))
    router.callback_query.register(decline_change_nickname, Text('decline:change:nickname'))

    router.callback_query.register(join_room, Text(startswith='join:room'))
    
    router.message.register(chatting, InRoom())
    

