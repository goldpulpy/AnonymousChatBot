from aiogram.types import BotCommand

ADMIN_COMMANDS = [
    BotCommand(
        command="start", 
        description="Запустить бота",
    ),
    BotCommand(
        command="stats", 
        description="Статистика",
    ),
    BotCommand(
        command="dump", 
        description="Выгрузка",
    ),
    BotCommand(
        command="mailing", 
        description="Рассылка",
    ),
    BotCommand(
        command="referrals", 
        description="Рефералы",
    ),
    BotCommand(
        command="sponsors", 
        description="Спонсоры",
    ),
    BotCommand(
        command="adverts", 
        description="Реклама",
    ),
    BotCommand(
        command="requests", 
        description="Заявки",
    ),
    BotCommand(
        command="money", 
        description="Прибыль",
    ),
    BotCommand(
        command="admin", 
        description="Выдать / убрать админку",
    ),
    BotCommand(
        command="ban",
        description="Заблокировать / Разблокировать пользователя",
    ),
    BotCommand(
        command="balance",
        description="Начислить / списать баланс для пользователя",
    ),
    BotCommand(
        command="vip",
        description="Выдать / снять VIP",
    ),
    BotCommand(
        command="dump_dialogue",
        description="Выгрузка диалога",
    )
]
