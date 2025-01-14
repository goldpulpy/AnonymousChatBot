"""VIP handlers"""

from aiogram import Router, types
from aiogram.filters import Text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from settings import VIP_OPTIONS
from app.filters import IsVip
from app.templates import texts
from app.templates.keyboards import user as nav
from app.utils.payments import BasePayment
from app.database.models import User, Bill


async def vip_menu(update: types.Message | types.CallbackQuery) -> None:
    """VIP menu"""
    if isinstance(update, types.CallbackQuery):
        update = update.message

    elif update.text in ('Поиск М 👨', 'Поиск Ж 👩'):
        await update.answer('Кажется, ваша VIP-подписка истекла...')

    await update.answer(
        texts.user.VIP,
        reply_markup=nav.inline.BUY,
    )


async def choose_bill(call: types.CallbackQuery) -> None:
    """Choose bill"""
    item_id = call.data.split(':')[1]

    await call.message.edit_text(
        "Выберите способ оплаты:",
        reply_markup=nav.inline.choose_bill(item_id),
    )


async def pre_balance_bill(call: types.CallbackQuery, user: User) -> None:
    """Pre balance bill"""
    item_id = call.data.split(':')[-1]
    item = VIP_OPTIONS[item_id]

    await call.message.edit_text(
        texts.user.BUY_VIP_BALANCE % (
            item['days'], item['price'], user.balance),
        reply_markup=nav.inline.confirm_buy_balance(item_id),
    )


async def balance_bill(
    call: types.CallbackQuery, session: AsyncSession, user: User,
) -> None:
    """Balance bill"""
    item_id = call.data.split(':')[-1]
    item = VIP_OPTIONS[item_id]

    user.balance -= item['price']
    if user.balance < 0:
        return await call.answer(
            '💰 Недостаточно средств, пожалуйста, пополните баланс', True
        )

    user.add_vip(VIP_OPTIONS[item_id]['days'])
    await session.commit()
    await call.message.delete()
    await call.message.answer(
        '<i>Поздравляем, теперь вы - VIP 👑</>!',
        reply_markup=nav.reply.main_menu(user),
    )


async def create_bill(call: types.CallbackQuery, payment: BasePayment) -> None:
    """Create bill"""
    item_id = call.data.split(':')[-1]
    item = VIP_OPTIONS[item_id]

    bill = await payment.create_payment(item['price'])
    await call.message.edit_text(
        texts.user.BILL,
        reply_markup=nav.inline.bill(bill, item_id),
    )


async def check_bill(
    call: types.CallbackQuery,
    session: AsyncSession,
    user: User,
    payment: BasePayment,
) -> None:
    """Check bill"""
    bill_id, item_id = call.data.split(':')[2:]
    bill_status = await payment.check_payment(int(bill_id))

    if not bill_status.is_paid:
        return await call.answer('Оплата еще не прошла❗', True)

    bill = await session.scalar(
        select(Bill)
        .where(Bill.id == int(bill_id))
    )

    if bill:
        return await call.answer('Этот счет слишком старый ⏲️', True)

    user.add_vip(VIP_OPTIONS[item_id]['days'])

    session.add(
        Bill(
            id=int(bill_id),
            user_id=user.id,
            amount=bill_status.amount,
            ref=user.ref,
        )
    )
    await session.commit()

    await call.message.delete()
    await call.message.answer(
        '<i>Поздравляем, теперь вы - VIP 👑</>!',
        reply_markup=nav.reply.main_menu(user),
    )


async def back_bill(call: types.CallbackQuery) -> None:
    """Back bill"""
    await call.message.edit_text(
        texts.user.VIP,
        reply_markup=nav.inline.BUY,
    )


async def referral(
    call: types.CallbackQuery, user: User, bot_info: types.User,
) -> None:
    """Referral"""
    await call.message.edit_text(
        texts.user.REF % (
            user.invited,
            bot_info.username,
            user.id,
        ),
        reply_markup=nav.inline.BACK_VIP,
        disable_web_page_preview=True,
    )


def register(router: Router) -> None:

    router.message.register(vip_menu, Text(
        [
            'Поиск М 👨',
            'Поиск Ж 👩',
            'Пошлый чат 🔞',
            'Поиск по полу ♂️',
            'Комнаты 🏠',
        ]
    ), IsVip(False))

    router.message.register(vip_menu, Text('VIP 👑'))
    router.callback_query.register(vip_menu, Text('vip'))
    router.callback_query.register(
        pre_balance_bill, Text(startswith='buy:balance'))
    router.callback_query.register(
        balance_bill, Text(startswith='accept:buy:balance'))
    router.callback_query.register(create_bill, Text(startswith='buy:url'))
    router.callback_query.register(choose_bill, Text(startswith='buy:'))
    router.callback_query.register(check_bill, Text(startswith='check:vip:'))
    router.callback_query.register(back_bill, Text('back:vip'))
    router.callback_query.register(referral, Text('ref'))
