from math import ceil

from app.utils import get_times
from app.templates import texts
from app.templates.keyboards import admin as nav
from app.database.models import User, Referral

from aiogram import Router, Bot, types
from aiogram.filters import Command, Text, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy import update, delete, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_ref_info(session: AsyncSession, ref: str, bot: Bot) -> list:
    
    unique = await session.scalar(
        select(func.count(User.id))
        .where(User.ref == ref)
    )
    alive = await session.scalar(
        select(func.count(User.id))
        .where(User.ref == ref)
        .where(User.block_date == None)
    )
    subbed = await session.scalar(
        select(func.count(User.id))
        .where(User.ref == ref)
        .where(User.subbed == True)
    )
    
    referral = await session.scalar(
        select(Referral)
        .where(Referral.ref == ref)
    )

    statements = (
        *(
            select(func.count(User.id))
            .where(User.ref == ref)
            .where(User.join_date >= date)
            for date in get_times()
        ),
    )

    return (
        ref,
        referral.total,
        unique,
        alive,
        subbed,
        *[
            await session.scalar(stmt)
            for stmt in statements
        ],
        referral.price,
        (round(referral.price / referral.total, 2) if unique else 'Н/д'),
        (round(referral.price / unique, 2) if unique else 'Н/д'),
        (round(referral.price / subbed, 2) if subbed else 'Н/д'),
        (await bot.me()).username,
        ref,
    )


async def get_refs(session: AsyncSession) -> list[str]:

    refs = await session.scalars(select(Referral.ref))
    return refs.all()


async def referral(message: types.Message, session: AsyncSession):

    await message.answer(
        texts.admin.REF_LIST,
        reply_markup=nav.inline.ref_list(
            await get_refs(session),
        )
    )


async def ref_list(call: types.CallbackQuery, session: AsyncSession, page: int):

    refs = await get_refs(session)

    if page < 1 or page > (ceil(len(refs)/9) or 1):

        return

    await call.message.edit_text(
        texts.admin.REF_LIST,
        reply_markup=nav.inline.ref_list(refs, page),
    )


async def ref(call: types.CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):

    action, ref = call.data.split(':')[1:3]

    if action == 'info':

        await call.message.edit_text(
            texts.admin.REF % await get_ref_info(session, ref, bot),
            reply_markup=nav.inline.ref(ref),
        )

    elif action == 'add':

        await state.set_state('ref.new')
        return await call.message.edit_text(
            texts.admin.REF_ADD,
            reply_markup=nav.inline.CANCEL,
        )

    elif action == 'del':

        await call.message.edit_text(
            texts.admin.REF_DEL % ref,
            reply_markup=nav.inline.choice(ref, 'ref'),
        )

    elif action == 'del2':

        await session.execute(
            delete(Referral)
            .where(Referral.ref == ref)
        )
        await session.execute(
            update(User)
            .where(User.ref == ref)
            .values(ref=None)
        )
        await session.commit()

        await call.message.edit_text(
            texts.admin.REF_LIST,
            reply_markup=nav.inline.ref_list(
                await get_refs(session),
            )
        )

    elif action == 'list':

        await ref_list(
            call, session, 
            page=(
                1 if not ref.isdigit() 
                else int(ref)
            ),
        )


async def create_ref(message: types.Message, state: FSMContext, session: AsyncSession):

    try:

        ref, price = message.text.split('\n')
        price = int(price)

    except ValueError:

        return await message.answer(
            'Ошибка введенных данных!',
            reply_markup=nav.inline.CANCEL,
        )

    await state.set_state()

    session.add(
        Referral(
            ref=ref,
            price=price,
        )
    )
    await session.commit()

    await referral(message, session)


async def cancel(call: types.CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession):

    await state.set_state()

    await ref_list(
        call, session, page=1,
    )


def register(router: Router):

    router.message.register(referral, Command("referrals"))
    router.message.register(referral, Text("Рефералы"))

    router.callback_query.register(ref, Text(startswith="ref:"))

    router.message.register(create_ref, StateFilter('ref.new'))
    router.callback_query.register(cancel, Text('cancel'), StateFilter('ref.new'))
