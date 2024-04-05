from app.database.models import Advert, Sponsor, RequestChannel, Room

from math import ceil
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def choice(item_id: int | str, prefix: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Да',
                    callback_data='%s:del2:%s' % (prefix, item_id),
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Нет',
                    callback_data='%s:info:%s' % (prefix, item_id),
                ),
            ],
        ],
    )


def channels(channels: list[RequestChannel]) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🟢' if channel.active else '⭕',
                    callback_data='request:active:%i' % channel.id,
                ),
                InlineKeyboardButton(
                    text=channel.title,
                    callback_data='none',
                ),
                InlineKeyboardButton(
                    text=str(channel.visits),
                    callback_data='none',
                ),
                InlineKeyboardButton(
                    text='🗑',
                    callback_data='request:del:%i' % channel.id,
                ),
            ] for channel in channels
        ]
    )


def ref(ref: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='ref:list:1',
                ),
                InlineKeyboardButton(
                    text='Удалить',
                    callback_data='ref:del:%s' % ref,
                ),
            ]
        ]
    )


def ref_list(refs: list[str], page: int=1) -> dict:

    pages = ceil(len(refs)/9) or 1
    refs = refs[(page - 1) * 9:page * 9]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *(
                [
                    InlineKeyboardButton(
                        text=ref,
                        callback_data='ref:info:%s' % ref,
                    ),
                ] for ref in refs
            ),
            [
                InlineKeyboardButton(
                    text='Добавить реф. ссылку',
                    callback_data='ref:add:',  # костыль
                ),
            ],
            [
                InlineKeyboardButton(
                    text='<-',
                    callback_data='ref:list:%i' % (page - 1),
                ),
                InlineKeyboardButton(
                    text='%i/%i' % (page, pages),
                    callback_data='none',
                ),
                InlineKeyboardButton(
                    text='->',
                    callback_data='ref:list:%i' % (page + 1),
                ),
            ],
        ],
    )


def sponsors(sponsors: list[Sponsor]) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *(
                [
                    InlineKeyboardButton(
                        text='🟢' if sponsor.is_active else '⭕',
                        callback_data='sponsor:active:%i' % sponsor.id,
                    ),
                    InlineKeyboardButton(
                        text=('🤖 ' if sponsor.is_bot else '💬 ') + sponsor.title,
                        callback_data='none',
                    ),
                    InlineKeyboardButton(
                        text='%i/%s' % (sponsor.visits, sponsor.limit or '∞'),
                        callback_data='none',
                    ),
                    InlineKeyboardButton(
                        text='🗑',
                        callback_data='sponsor:del:%i' % sponsor.id,
                    ),
                ] for sponsor in sponsors
            ),
            [
                InlineKeyboardButton(
                    text='Добавить',
                    callback_data='sponsor:add',
                ),
            ],
        ],
    )


def adverts(adverts: list[Advert]) -> dict:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *(
                [
                    InlineKeyboardButton(
                        text='🟢' if advert.is_active else '⭕',
                        callback_data='ad:status:%i' % advert.id,
                    ),
                    InlineKeyboardButton(
                        text=advert.title,
                        callback_data='ad:show:%i' % advert.id,
                    ),
                    InlineKeyboardButton(
                        text='%i/%s' % (advert.views, advert.target or '∞'),
                        callback_data='none',
                    ),
                    InlineKeyboardButton(
                        text='🗑',
                        callback_data='ad:del:%i' % advert.id,
                    ),
                ] for advert in adverts
            ),
            [
                InlineKeyboardButton(
                    text='Добавить',
                    callback_data='ad:add',
                ),
            ],
        ],
    )

def rooms(rooms: list[Room]) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *(
                [
                    InlineKeyboardButton(
                        text='🏠 %s' % room.room_name,
                        callback_data='room:info:%i' % room.id,
                    ),
                    InlineKeyboardButton(
                        text='👤 %i/%s' % (room.room_online_members, room.room_online_limit if room.room_online_limit != 0 else '∞'),
                        callback_data='room:members:%i' % room.id,
                    ),
                    InlineKeyboardButton(
                        text='🗑',
                        callback_data='room:del:%i' % room.id,
                    ),
                ] for room in rooms
            ),
            [
                InlineKeyboardButton(
                    text='Добавить',
                    callback_data='room:add',
                )
            ],
        ],
)


def room_info(room: Room) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text= 'Удалить комнату🗑',
                    callback_data='room:del:%i' % room.id,

                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='room:back',
                )
            ],
        ],
    )

DUMP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Всех',
                callback_data='dump:dead',
            ),
            InlineKeyboardButton(
                text='Живых',
                callback_data='dump:alive',
            ),
            InlineKeyboardButton(
                text='Обычных',
                callback_data='dump:vip',
            ),
        ],  
    ],
)

CANCEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Отмена',
                callback_data='cancel',
            ),
        ],
    ],
)

SPONSOR_CHOICE = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🤖 Бот',
                callback_data='addsponsor:bot',
            ),
            InlineKeyboardButton(
                text='💬 Канал',
                callback_data='addsponsor:channel',
            ),
        ],
    ],
)

STOPMAIL = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Остановить рассылку',
                callback_data='stopmail',
            ),
        ],
    ],
)
