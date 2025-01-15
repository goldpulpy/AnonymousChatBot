"""Settings for the bot"""
VIP_OPTIONS = {
    'day': {
        'name': '🔥 На день - 39 руб.',
        'price': 39,
        'days': 1,
    },
    'week': {
        'name': 'На неделю - 129 руб.',
        'price': 129,
        'days': 7,
    },
    'month': {
        'name': 'На месяц - 249 руб.',
        'price': 249,
        'days': 31,
    },
    'year': {
        'name': 'На год - 599 руб.',
        'price': 599,
        'days': 365,
    },
}
SHOW_CONTACTS_PRICE: int = 10  # Цена за показ контактов
CHANGE_NICKNAME_IN_ROOM_PRICE: int = 10  # Цена за смену никнейма в комнате
