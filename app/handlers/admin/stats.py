from app.database.models import User, Dialogue, Bill
from app.templates import texts
from app.utils import get_times, plots

from aiogram import Router, types
from aiogram.filters import Text, Command

from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def user_stats(message: types.Message, session: AsyncSession):

    statements = (
        select(func.count(User.id)).where(User.chat_only == False, User.id > 0),
        select(func.count(User.id)).where(User.block_date == None, User.chat_only == False),
        select(func.count(User.id)).where(User.block_date != None, User.chat_only == False),
        select(func.count(User.id)).where(User.subbed == True, User.chat_only == False),
        select(func.count(User.id)).where(User.id < 0),
        select(func.count(Dialogue.first)).where(Dialogue.first != Dialogue.second, 
                                                 Dialogue.first > 0, Dialogue.second > 0),
        *(
            select(func.count(User.id))
            .where(User.join_date >= date, User.chat_only == False)
            for date in get_times()
        ),
        *(
            select(func.count(User.id))
            .where(User.join_date >= date, User.chat_only == False)
            .where(User.ref == None)
            for date in get_times()
        ),
    )

    results = [
        await session.scalar(stmt)
        for stmt in statements
    ]

    text = texts.admin.STATS % tuple(results)
    msg = await message.answer_animation(
        'https://media.tenor.com/kOosNeYUmWkAAAAC/loading-buffering.gif', 
        caption=text,
    )
    image = await plots.UsersPlot.create_plot(session)

    await msg.edit_media(
        types.InputMediaPhoto(
            media=types.BufferedInputFile(image.read(), 'plot.png'), 
            caption=text,
        )
    )


async def payment_stats(message: types.Message, session: AsyncSession):

    statements = [
            select(func.sum(Bill.amount))
            .where(Bill.date >= date)
            for date in get_times()
    ]
    results = [
        await session.scalar(stmt) or 0
        for stmt in statements
    ]

    msg = await message.answer_animation(
        'https://media.tenor.com/kOosNeYUmWkAAAAC/loading-buffering.gif',
        caption=texts.admin.MONEY % tuple(results),
    )
    image = await plots.PaymentPlot.create_plot(session)

    await msg.edit_media(
        types.InputMediaPhoto(
            media=types.BufferedInputFile(image.read(), 'plot.png'),
            caption=texts.admin.MONEY % tuple(results),
        )
    )
    

def register(router: Router):

    router.message.register(user_stats, Text("Статистика"))
    router.message.register(user_stats, Command("stats"))

    router.message.register(payment_stats, Text('Прибыль'))
    router.message.register(payment_stats, Command("money"))
