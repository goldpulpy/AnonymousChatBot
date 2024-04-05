import asyncio

from app.filters import ContentTypes
from app.utils.mailing import MailerSingleton
from app.database.models import User
from app.templates.keyboards import admin as nav

from datetime import datetime

from aiogram import Router, Bot, types
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def pre_mailing(message: types.Message, state: FSMContext):
    
    await message.answer(
        "Что вы хотите отправить?",
        reply_markup=nav.inline.CANCEL,
    )
    await state.set_state("mailing.text")


async def mailing_text(message: types.Message, state: FSMContext):

    await state.update_data(
        message_id=message.message_id,
        reply_markup=(
            message.reply_markup.dict()
            if message.reply_markup else None
        ),
    )

    await message.copy_to(
        message.from_user.id,
        reply_markup=message.reply_markup,
    )
    await message.answer(
        "Начинаю рассылку?",
        reply_markup=nav.reply.CONFIRM,
    )

    await state.set_state("mailing.confirm")


async def mailing_confirm(message: types.Message, bot: Bot, state: FSMContext, session: AsyncSession):

    if message.text == 'Подтвердить':

        data = await state.get_data()
        scope = (await session.scalars(
            select(User.id)
            .where(User.block_date == None)
            .where(User.chat_only == False)
            .where(User.vip_time < datetime.now())
        )).all()

        await message.answer(
            'Начинаю рассылку...',
            reply_markup=nav.reply.MENU,
        )

        mailer = MailerSingleton.get_instance()
        asyncio.create_task(mailer.start_mailing(
            data['message_id'], data['reply_markup'], 
            message.chat.id, bot, scope,
            cancel_keyboard=nav.inline.STOPMAIL,
        ))

    else:

        await message.answer("Рассылка отменена.", reply_markup=nav.reply.MENU)

    await state.clear()


async def stop_mailing(call: types.CallbackQuery):

    MailerSingleton.get_instance().stop_mailing()
    
    await call.message.delete()
    await call.answer("Рассылка остановлена.")


async def cancel_mailing(call: types.CallbackQuery, state: FSMContext):

    await state.clear()

    await call.message.delete()
    await call.answer("Отменено.")


def register(router: Router):

    router.message.register(pre_mailing, Command("mailing"))
    router.message.register(pre_mailing, Text("Рассылка"))

    router.message.register(mailing_text, StateFilter("mailing.text"), ContentTypes(types.ContentType.ANY))
    router.callback_query.register(cancel_mailing, Text("cancel"), StateFilter("mailing.text"))

    router.message.register(mailing_confirm, StateFilter("mailing.confirm"))

    router.callback_query.register(stop_mailing, Text("stopmail"))
    