import json

from app.filters import ContentTypes
from app.templates import texts
from app.templates.keyboards import admin as nav
from app.database.models import Advert, History

from aiogram import Router, types
from aiogram.filters import Text, Command, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_adverts(session: AsyncSession) -> list[Advert]:

    result = await session.scalars(
        select(Advert)
    )
    return result.all()


async def ads_menu(message: types.Message, session: AsyncSession, edit: bool=False):

    method = message.edit_text if edit else message.answer
    await method(
        '📌 Список рекламных постов',
        reply_markup=nav.inline.adverts(
            await get_adverts(session),
        )
    )


async def ad(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    action = call.data.split(':')[1]

    if action == 'add':

        await call.message.edit_text(
            texts.admin.ADS_ADD,
            reply_markup=nav.inline.CANCEL,
        )
        return await state.set_state('adverts.add.title')

    ad_id = int(call.data.split(':')[2])
    ad: Advert = await session.scalar(
        select(Advert)
        .where(Advert.id == ad_id)
    )

    if action == 'show':

        METHODS = (
            None,
            call.message.answer_photo,
            call.message.answer_video,
            call.message.answer_animation,
            call.message.answer_audio,
            call.message.answer_voice,
        )

        if ad.type == 0:

            await call.message.answer(
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
                ad.file_id,
                caption=ad.text,
                reply_markup=(
                    json.loads(ad.markup)
                    if ad.markup else None
                ),
                disable_notification=True,
            )

    if action == 'status':

        if ad.is_active and ad.views >= ad.target and ad.target != 0:
            
            ad.views = 0

        ad.is_active = not ad.is_active

    elif action == 'del':

        return await call.message.edit_text(
            'Вы уверены, что хотите удалить рекламу?',
            reply_markup=nav.inline.choice(ad_id, 'ad'),
        )

    elif action == 'del2':

        await session.delete(ad)
        await session.execute(
            delete(History)
            .where(History.ad_id == ad_id)
        )

    await session.commit()
    await ads_menu(call.message, session, edit=True)


async def add_ad_params(message: types.Message, state: FSMContext):

    try:

        title, target = message.text.split('\n')
        target = int(target)

    except ValueError:

        return await message.answer(
            'Неверный формат данных!',
            reply_markup=nav.inline.CANCEL,
        )

    await state.update_data(
        title=title,
        target=target,
    )

    await message.answer(
        'Отправьте рекламный пост',
        reply_markup=nav.inline.CANCEL,
    )
    await state.set_state('adverts.add.text')


async def add_ad_text(message: types.Message, state: FSMContext, session: AsyncSession):

    data = await state.get_data()

    file_id = None
    type_ = 0

    if message.photo:

        file_id = message.photo.pop().file_id
        type_ = 1

    elif message.video:

        file_id = message.video.file_id
        type_ = 2

    elif message.animation:

        file_id = message.animation.file_id
        type_ = 3

    elif message.audio:

        file_id = message.audio.file_id
        type_ = 4

    elif message.voice:

        file_id = message.voice.file_id
        type_ = 5

    ad = Advert(
        title=data['title'],
        target=data['target'],
        text=message.html_text,
        file_id=file_id,
        type=type_,
        markup=(
            None if not message.reply_markup 
            else message.reply_markup.json() 
        )
    )

    session.add(ad)
    await session.commit()

    await ads_menu(message, session)
    await state.clear()


async def cancel(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):

    await ads_menu(call.message, session)
    await state.clear()


def register(router: Router):

    router.message.register(ads_menu, Text('Посты'))
    router.message.register(ads_menu, Command('adverts'))

    router.callback_query.register(ad, Text(startswith='ad:'))

    router.message.register(add_ad_params, StateFilter('adverts.add.title'))
    router.message.register(add_ad_text, StateFilter('adverts.add.text'), ContentTypes(types.ContentType.ANY))

    router.callback_query.register(cancel, Text('cancel'), StateFilter('adverts.add.title'))
    router.callback_query.register(cancel, Text('cancel'), StateFilter('adverts.add.text'))
