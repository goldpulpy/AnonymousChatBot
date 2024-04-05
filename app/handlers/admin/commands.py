from app.utils import set_commands
from app.utils.config import Settings
from app.database.models import User, DialogueHistory
from app.templates.keyboards import admin as nav

from aiogram import Router, Bot, types
from aiogram.filters import Command

from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from io import BytesIO
import os

async def give_admin(message: types.Message, bot: Bot, session: AsyncSession, config: Settings):

    if message.from_user.id not in config.bot.admins:

        return

    try:

        user_id = int(message.text.split(' ')[1])

    except (IndexError, ValueError):

        return await message.answer(
            'Пример использования команды: <code>/admin &lt;user_id&gt;</code>',
        )

    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
    )

    if not user:

        return await message.answer(
            'Пользователь с таким id не найден в базе.',
        )

    user.is_admin = not user.is_admin
    await session.commit()

    await message.answer(
        '%s админку пользователя %i' % (
            ('Выдал' if user.is_admin else 'Убрал'),
            user.id,
        ),
    )
    await set_commands(bot, config, session=session)


async def give_ban(message: types.Message, bot: Bot, session: AsyncSession, config: Settings):

    try: user_id: int = int(message.text.split(' ')[1])
    except (IndexError, ValueError):

        return await message.answer(
            'Пример использования команды: <code>/ban *&lt;user_id&gt; &lt;reason&gt;</code>',
        )


    try: reason: str = ' '.join(message.text.split(' ')[2:])
    except reason: bool = False

    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
    )

    if not user:

        return await message.answer(
            'Пользователь с таким id не найден в базе.',
        )

    user.is_banned = not user.is_banned
    await session.commit()

    await message.answer(
        '%s бан пользователю %i' % (
            ('Выдан' if user.is_banned else 'Снят'),
            user.id,
        ),
    )
    
    await bot.send_message(
        user.id,
        '<b>%s Вы были %s администрацией</b> %s' % (
            '⛔️' if user.is_banned else '✅',
            'заблокированы' if user.is_banned else 'разблокированы',
            '' if not reason else f'\n💬 Причина: {reason}')
    )


async def give_vip(message: types.Message, session: AsyncSession):

    try: 
        
        user_id: int = int(message.text.split(' ')[1])
        days: int = int(message.text.split(' ')[2])

    except (IndexError, ValueError):

        return await message.answer(
            'Пример использования команды: <code>/vip &lt;user_id&gt; &lt;days&gt;</code>',
        )

    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
    )

    if not user:

        return await message.answer(
            'Пользователь с таким id не найден в базе.',
        )



    days_is_negative: bool = days < 0

    user.add_vip(days)

    await session.commit()

    await message.answer(
        '%s VIP дней пользователю %i, %id' % (
            'Выдано' if not days_is_negative else 'Снято',
            int(user.id), days)
    )

async def add_balance(message: types.Message, session: AsyncSession):

    try: 
        
        user_id: int = int(message.text.split(' ')[1])
        amount: int = int(message.text.split(' ')[2])

    except (IndexError, ValueError):

        return await message.answer(
            'Пример использования команды: <code>/balance &lt;user_id&gt; &lt;amount&gt;</code>',
        )

    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
    )

    if not user:

        return await message.answer(
            'Пользователь с таким id не найден в базе.',
        )

    amount_is_negative: bool = amount < 0

    user.balance += amount

    if amount_is_negative:

        user.balance = max(0, user.balance)


    await session.commit()

    await message.answer(
        'Пользователю %i %s %i ₽' % (
            user.id,
            'списано'  if amount_is_negative else 'добавлено',
            amount)
    )



async def dump_dialogue(message: types.Message, session: AsyncSession):
    try: 
        
        target_id: int = int(message.text.split(' ')[1].split(':')[1])
        method = message.text.split(' ')[1].split(':')[0]

    except (IndexError, ValueError):

        return await message.answer(
            'Пример использования команды: <code>/dump_dialogue &lt;user:user_id&gt; или &lt;dialogue:dialogue_id&gt;</code>',
        )

    if method not in ["user", "dialogue"]:

        return await message.answer(
            'Пример использования команды: <code>/dump_dialogue &lt;user:user_id&gt; или &lt;dialogue:dialogue_id&gt;</code>',
        )
    
    file = BytesIO()

    if method == "dialogue":
    
        dialogues = await session.scalars(
            select(DialogueHistory)
            .where(DialogueHistory.dialogue_id == target_id)
        )


    else:

        dialogues = await session.scalars(
            select(DialogueHistory)
            .where(or_(
                DialogueHistory.first == target_id,
                DialogueHistory.second == target_id)
                )
        )

    

    lines = (
        "%s - [Диалог: %s] - [%s] -> [%s]: %s%s\n" % (
            dialogue.time.strftime('%d.%m.%Y %H:%M:%S'),
            dialogue.dialogue_id,
            dialogue.first,
            dialogue.second,
            '%s ' % dialogue.message if dialogue.message else '',
            '(фото: %s)' % dialogue.image_id if dialogue.image_id else '',
        ) for dialogue in dialogues
    )

    file.writelines(line.encode() for line in lines) 


    file.seek(0, os.SEEK_END)

    if file.tell() == 0:
        return await message.answer('Диалог не содержит ни одного сообщения')


    file.seek(0)

    await message.answer_document(
        types.BufferedInputFile(file.read(), f'dialogue_history.txt'),
        caption=f"Диалог успешно выгружен",
    )




def register(router: Router):

    router.message.register(give_admin, Command('admin'))
    router.message.register(give_vip, Command('vip'))
    router.message.register(give_ban, Command('ban'))
    router.message.register(add_balance, Command('balance'))
    router.message.register(dump_dialogue, Command('dump_dialogue'))