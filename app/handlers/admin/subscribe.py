"""Subscribe handlers"""
import validators

from aiogram import Router, types
from aiogram.filters import Text, StateFilter, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.templates import texts
from app.templates.keyboards import admin as nav
from app.database.models import Sponsor


async def get_channels(session: AsyncSession) -> list[Sponsor]:
    """Get channels handler"""
    channels = await session.scalars(
        select(Sponsor)
    )
    return channels.all()


async def update_sponsors(
    message: types.Message, session: AsyncSession,
) -> None:
    """Update sponsors handler"""
    await message.edit_text(
        texts.admin.SPONSORS,
        reply_markup=nav.inline.sponsors(
            await get_channels(session),
        ),
    )


async def channels(
    message: types.Message, session: AsyncSession,
) -> None:
    """Channels handler"""
    await message.answer(
        texts.admin.SPONSORS,
        reply_markup=nav.inline.sponsors(
            await get_channels(session)
        ),
    )


async def sponsor_menu(
    call: types.CallbackQuery, session: AsyncSession,
) -> None:
    """Sponsor menu handler"""
    action, *args = call.data.split(":", 2)[1:]

    if action == "info":
        return await update_sponsors(call.message, session)

    elif action == "add":
        return await call.message.edit_text(
            texts.admin.PRE_CHANNEL_ADD,
            reply_markup=nav.inline.SPONSOR_CHOICE,
        )

    sponsor = await session.scalar(
        select(Sponsor).where(
            Sponsor.id == int(args[0]),
        )
    )

    if action == "del":
        return await call.message.edit_text(
            texts.admin.SPONSOR_DEL % sponsor.title,
            reply_markup=nav.inline.choice(
                args[0], 'sponsor',
            ),
        )

    elif action == "del2":
        await call.answer(
            "Спонсор %s удален." % sponsor.title,
            show_alert=True,
        )
        await session.delete(sponsor)

    if action == "active":
        if sponsor.visits >= sponsor.limit and sponsor.limit != 0:
            sponsor.visits = 0
        sponsor.is_active = not sponsor.is_active

    await session.commit()
    await update_sponsors(call.message, session)


async def choice_sponsor(
    call: types.CallbackQuery, state: FSMContext,
) -> None:

    await call.message.edit_text(
        texts.admin.CHANNEL_ADD,
        reply_markup=nav.inline.CANCEL,
    )
    await state.set_state('sponsor.add')
    await state.update_data(
        is_bot=(call.data.split(":")[1] == 'bot'),
    )


async def sponsor_add(
    message: types.Message, state: FSMContext, session: AsyncSession,
) -> None:

    try:

        access, title, link, enable, limit = message.text.splitlines()
        limit = int(limit)

        if not validators.url(link):
            return await message.answer(
                "Вы ошиблись при вводе ссылки.",
                reply_markup=nav.inline.CANCEL,
            )

    except ValueError:
        return await message.answer(
            "Неверный формат.",
            reply_markup=nav.inline.CANCEL,
        )

    data = await state.get_data()
    session.add(
        Sponsor(
            access_id=access,
            title=title,
            link=link,
            is_bot=data['is_bot'],
            check=(enable == '1'),
            limit=limit,
        )
    )
    await session.commit()

    await message.answer(
        texts.admin.SPONSORS,
        reply_markup=nav.inline.sponsors(
            await get_channels(session),
        ),
    )


async def cancel(
    call: types.CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    await update_sponsors(call.message, session)
    await state.clear()


def register(router: Router) -> None:
    """Register admin subscribe handlers"""
    router.message.register(channels, Text("Спонсоры"))
    router.message.register(channels, Command("sponsors"))
    router.callback_query.register(sponsor_menu, Text(startswith="sponsor"))
    router.callback_query.register(
        choice_sponsor, Text(startswith="addsponsor")
    )
    router.message.register(sponsor_add, StateFilter("sponsor.add"))
    router.callback_query.register(
        cancel, Text('cancel'), StateFilter("sponsor.add")
    )
