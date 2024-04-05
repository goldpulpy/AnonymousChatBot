from app.templates.keyboards import admin as nav
from app.templates.keyboards import user as nav_user
from app.database.models import Room, User
from app.templates import texts

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, Text, StateFilter
from aiogram.utils.markdown import hlink

from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession





async def rooms(message: types.Message, session: AsyncSession):

    rooms = await session.scalars(
        select(Room)
    )


    await message.answer(
        'Список комнат:',
        reply_markup=nav.inline.rooms(rooms),
    )


async def room_back(call: types.CallbackQuery, session: AsyncSession):
    rooms = await session.scalars(
        select(Room)
    )


    await call.message.edit_text(
        'Список комнат:',
        reply_markup=nav.inline.rooms(rooms),
    )


async def room_info(call: types.CallbackQuery, session: AsyncSession):

    room_id = int(call.data.split(':')[-1])

    room = await session.get(Room, room_id)

    await call.message.edit_text(
        texts.admin.ROOM_INFO % (
            room.room_name,
            room.room_online_members,
            room.room_online_limit if room.room_online_limit != 0 else '∞',
        ),
        reply_markup=nav.inline.room_info(room),
    )


async def room_members(call: types.CallbackQuery, session: AsyncSession):

    room_id = int(call.data.split(':')[-1])

    members_list = []

    room = await session.get(Room, room_id)


    online_members = room.get_online_members()
    online_members_nickname = room.get_online_members_nickname()

    for member in range(len(online_members)):

        user = await session.get(User, online_members[member])

        members_list.append(
        "ID: %s | Имя: %s | Никнейм: %s" % (
            hlink(str(user.id), 'tg://user?id=' + str(user.id)), 
            user.first_name, 
            online_members_nickname[member])
        )


    await call.message.edit_text(

        f'👤 Список участников комнаты {room.room_name}:\n' + '\n'.join(members_list),
        reply_markup=nav.inline.room_info(room),
    )


async def pre_add_room(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):

    await call.message.edit_text(
        texts.admin.ROOM_ADD,
        reply_markup=nav.inline.CANCEL,
    )
    
    await state.set_state('room.add')



async def add_room(message: types.Message, state: FSMContext, session: AsyncSession):

    try:

        room_name, max_members = message.text.splitlines()
        max_members = int(max_members)
        
    except ValueError:

        return await message.answer(
            "Неверный формат.", 
            reply_markup=nav.inline.CANCEL,
        )
    
    await state.clear()

    session.add(
        Room(
            room_name=room_name,
            room_online_limit=max_members,
        )
    )

    await session.commit()


    await rooms(message, session)





async def pre_delete_room(call: types.CallbackQuery, session: AsyncSession):

    room_id = int(call.data.split(':')[-1])


    room = await session.get(Room, room_id)

    await call.message.edit_text(
        f'Вы действительно хотите удалить комнату <code>{room.room_name}</code>?',
        reply_markup=nav.inline.choice(int(room_id), 'room'),
        
    )


async def delete_room(call: types.CallbackQuery, session: AsyncSession, bot: Bot):


    room_id = int(call.data.split(':')[-1])

    room = await session.get(Room, room_id)

    await session.execute(
        delete(Room)
        .where(Room.id == room_id)
    )

    await session.commit()


    await call.message.edit_text(
        f'Комната <code>{room.room_name}</code> удалена.',
        
    )

    members = room.get_online_members()


    for member in members:

        try:

            user = await session.get(User, member)

            await bot.send_message(user.id, 
            f'🏠 Комната <code>{room.room_name}</code> удалена.',
            reply_markup=nav_user.reply.main_menu(user),)

            user.in_room = 0

            await session.commit()

        except:

            pass

    await rooms(call, session)





async def cancel(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    await rooms(call.message, session)
    await state.clear()




def register(router: Router):


    router.message.register(rooms, Text("Управление комнатами"))

    router.callback_query.register(room_back, Text("room:back"))

    router.callback_query.register(pre_add_room, Text("room:add"))
    router.message.register(add_room, StateFilter("room.add"))

    router.callback_query.register(delete_room, Text(startswith="room:del2"))
    router.callback_query.register(pre_delete_room, Text(startswith="room:del"))

    router.callback_query.register(room_info, Text(startswith="room:info"))
    router.callback_query.register(room_members, Text(startswith="room:members"))

    router.callback_query.register(cancel, Text('cancel'), StateFilter("room.add"))