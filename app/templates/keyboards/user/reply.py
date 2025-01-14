"""User keyboards"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.database.models import User


def main_menu(user: User) -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    if user.is_vip:
        return VIP_MENU
    return USER_MENU  # VIP_MENU


VIP_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Случайный диалог 🔍'),
        ],
        [
            KeyboardButton(text='Поиск Ж 👩'),
            KeyboardButton(text='Поиск М 👨'),
        ],
        [
            KeyboardButton(text='Пошлый чат 🔞'),
            KeyboardButton(text='Профиль 👤'),
        ],
        [
            KeyboardButton(text='Комнаты 🏠'),
            KeyboardButton(text='Мои друзья 👥'),
        ],
        [
            KeyboardButton(text='VIP 👑'),
        ],
    ],
    resize_keyboard=True,
)
USER_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Случайный диалог 🔍'),
        ],
        [
            KeyboardButton(text='Поиск по полу ♂️'),
        ],
        [
            KeyboardButton(text='Пошлый чат 🔞'),
            KeyboardButton(text='Профиль 👤'),
        ],
        [
            KeyboardButton(text='Комнаты 🏠'),
            KeyboardButton(text='Мои друзья 👥'),
        ],
        [
            KeyboardButton(text='VIP 👑'),
        ],
    ],
    resize_keyboard=True,
)

DIALOGUE_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Завершить диалог 🚫'),
        ],
        [
            KeyboardButton(text='Добавить в друзья 👥'),
        ],
        [
            KeyboardButton(text='Показать контакты 📱'),
        ],
        [
            KeyboardButton(text='Пожаловаться 💬'),
        ]
    ],
    resize_keyboard=True,
)

DIALOGUE_FRIEND_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Завершить диалог 🚫'),
        ],
        [
            KeyboardButton(text='Показать контакты 📱'),
        ],
        [
            KeyboardButton(text='Пожаловаться 💬'),
        ]
    ],
    resize_keyboard=True,
)


ROOM_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Выйти из комнаты 🚪'),
        ],
        [
            KeyboardButton(text='Участники 👤'),
        ],
        [
            KeyboardButton(text='Сменить ник в комнате 🔄'),
        ],
    ],
    resize_keyboard=True,
)


JOIN_REQUEST = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🛥️'),
            KeyboardButton(text='👾'),
            KeyboardButton(text='🏎️'),
        ],
        [
            KeyboardButton(text='🌐'),
            KeyboardButton(text='🛩️'),
            KeyboardButton(text='⏳'),
        ],
    ],
)
