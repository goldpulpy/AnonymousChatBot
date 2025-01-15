"""Admin keyboards"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


CONFIRM = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Подтвердить'),
            KeyboardButton(text='Отмена'),
        ],
    ],
    resize_keyboard=True,
)

MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Статистика'),
            KeyboardButton(text='Посты'),
            KeyboardButton(text='Прибыль'),
        ],
        [
            KeyboardButton(text='Рассылка'),
            KeyboardButton(text='Спонсоры'),
            KeyboardButton(text='Заявки'),
        ],
        [
            KeyboardButton(text='Выгрузка'),
            KeyboardButton(text='Рефералы'),
        ],
        [
            KeyboardButton(text='Управление комнатами'),
        ],

    ],
    resize_keyboard=True,
)
