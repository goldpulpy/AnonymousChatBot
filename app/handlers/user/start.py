from app.filters import IsVip, IsRegistered
from app.templates import texts
from app.templates.keyboards import user as nav
from app.database.models import Referral, User
from app.handlers.user.dialogue import delete_dialogue

from aiogram import Router, types, Bot
from aiogram.filters import CommandStart, Text, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.user.rooms import leave_room

async def start(message: types.Message, bot: Bot, command: CommandObject, session: AsyncSession, user: User, state: FSMContext):

    if user.in_room != 0:

        await leave_room(message, session, bot, user)
    
    if user.is_man is None:

        await state.set_state('start')
        await message.answer(
            '<i><b>Добро пожаловать в анонимный чат! Выбери свой пол:</></>',
            reply_markup=nav.inline.GENDER,
        )

    else:

        await message.answer(
            texts.user.START, 
            reply_markup=nav.reply.main_menu(user),
        )

        if user.partner:

            await delete_dialogue(session, message.from_user.id)

    if not command.args:

        return

    await session.execute(
        update(Referral)
        .where(Referral.ref == command.args)
        .values(total=Referral.total + 1)
    )
    await session.commit()


async def pre_reg(message: types.Message, state: FSMContext):

    await state.set_state('start')
    await message.answer(
        '<i><b>Добро пожаловать в анонимный чат! Выбери свой пол:</></>',
        reply_markup=nav.inline.GENDER,
    )


def register(router: Router):

    router.message.register(start, CommandStart())
    router.message.register(start, Text('Поиск по полу ♂️'), IsVip())

    router.message.register(pre_reg, IsRegistered(False))
