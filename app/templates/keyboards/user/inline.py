from settings import VIP_OPTIONS
from app.database.models import Sponsor
from app.utils.payments import BaseBill

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def split(items: list, size: int) -> list[list]:

    return [
        items[index:index + size] 
        for index in range(0, len(items), size)
    ]


def subscription(sponsors: list[Sponsor]) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *(
                [
                    InlineKeyboardButton(
                        text=sponsor.title,
                        url=sponsor.link,
                    ),
                ] for sponsor in sponsors
            ),
            [
                InlineKeyboardButton(
                    text='Проверить подписку',
                    callback_data='checksub',
                ),
            ],
        ]
    )


def bill(bill: BaseBill, item_id: str, is_vip: bool = True) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Оплатить 🔗',
                    url=bill.url,
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Проверить ✅',
                    callback_data='check:%s:%i:%s' % (
                        'vip' if is_vip else 'profile',
                        bill.id, item_id,
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад 🔙',
                    callback_data='back:vip' if is_vip else 'back:profile',
                ),
            ],
        ]
    )

def choose_bill(item_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Оплатить балансом 💰',
                callback_data='buy:balance:%s' % item_id,
            )
        ],
        [
            InlineKeyboardButton(
                text='Оплатить cсылкой 🔗',
                callback_data='buy:url:%s' % item_id,
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад 🔙',
                callback_data='back:vip',
            ),
        ],
    ]
)

def confirm_buy_balance(item_id) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Подтвердить✅',
                    callback_data='accept:buy:balance:%s' % item_id,
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад 🔙',
                    callback_data='back:vip',
                ),
            ],
        ]
    )


BUY = InlineKeyboardMarkup(
    inline_keyboard=[
        *(
            [
                InlineKeyboardButton(
                    text=item['name'],
                    callback_data='buy:%s' % key,
                ),
            ] for key, item in VIP_OPTIONS.items()
        ),
        [
            InlineKeyboardButton(
                text='Получить бесплатно 🤫',
                callback_data='ref',
            ),
        ],
    ],
)

ADULT_GENDER = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Муж. ♂️',
                callback_data='adult:male',
            ),
            InlineKeyboardButton(
                text='Жен. ♀️',
                callback_data='adult:female',
            ),
        ]
    ],
)

BACK_VIP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад 🔙',
                callback_data='back:vip',
            ),
        ],
    ],
)

PROFILE = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Изменить пол👩‍❤️‍👨',
                callback_data='edit:gender',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Изменить возраст📝',
                callback_data='edit:age',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Пополнить баланс💰',
                callback_data='add:balance',
            ),
        ],
    ],
)
GENDER = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Парень🙋‍♂',
                callback_data='gender:1',
            ),
            InlineKeyboardButton(
                text='Девушка🙎‍♀',
                callback_data='gender:0',
            ),
        ],
    ],
)

SHOW_CONTACTS = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Показать',
                callback_data='show:contacts',
            ),
        ],
    ],
)

FRIEND_REQUEST = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Принять✅',
                callback_data='accept:friend',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Отклонить❌',
                callback_data='decline:friend',
            ),
        ],
    ],
)

COMPLAINT = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Отправить✅',
                callback_data='accept:complaint',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Отменить❌',
                callback_data='decline:complaint',
            ),
        ],
    ],
)


PRE_CHANGE_NICKNAME = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Сменить никнейм🔄',
                callback_data='change:nickname',
            ),
        ],
    ],
)

def change_nickname(new_nickname: dict) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Подтвердить✅',
                    callback_data='accept:change:nickname:%s' % new_nickname,
                )
            ],
            [
                InlineKeyboardButton(
                    text='Отменить❌',
                    callback_data='decline:change:nickname',
                )
            ]
        ]
    )


def friends(friends_list: dict) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='%s - %s' %  (friend['status'], friend['user'].first_name),
                    callback_data='friend:get:%i' % friend['user'].id,
                )
            ] for friend in friends_list
        ]
    )


def friend(friend_id: dict) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Пригласить в диалог💬',
                    callback_data='friend:dialogue:%i' % friend_id,
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data='friend:back',
                )
            ]
        ]
    )

def friend_dialogue_request(friend_id: int) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Принять✅',
                    callback_data='accept:dialogue:friend:%s' % friend_id,
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Отклонить❌',
                    callback_data='decline:dialogue:friend:%s' % friend_id,
                ),
            ],
        ],
    )


def room_list(rooms: list) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 [%s/%s] %s" % (room.room_online_members,
                    room.room_online_limit if room.room_online_limit != 0 else '∞',
                    room.room_name),
                    callback_data='join:room:%i' % room.id,
                )
            ] for room in rooms
        ]
    )
