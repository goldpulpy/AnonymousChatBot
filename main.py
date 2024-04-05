import os
import time
import asyncio
import logging

from app import middlewares, handlers
from app.database import create_sessionmaker
from app.utils import set_commands, load_config, schedule, payments

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage


log = logging.getLogger(__name__)

async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger(
        'aiogram.event',
    ).setLevel(logging.WARNING)

    log.info("Starting bot...")
    config = load_config()

    os.environ['TZ'] = config.bot.timezone
    time.tzset()

    log.info('Set timesone to "%s"' % config.bot.timezone)

    if config.bot.use_redis:

        storage = RedisStorage.from_url(
            'redis://%s:6379/%i' % (
                config.redis.host,
                config.redis.db,
            ),
        )

    else:

        storage = MemoryStorage()

    sessionmaker = await create_sessionmaker(config.db)
    payment = (
        payments.BasePayment() if not config.payments.enabled
        else payments.PayOK(
            config.payments.api_id,
            config.payments.api_key,
            config.payments.project_id,
            config.payments.project_secret,
        )
    )

    bot = Bot(
        token=config.bot.token,
        parse_mode="HTML",
    )
    dp = Dispatcher(storage=storage)

    middlewares.setup(dp, sessionmaker)
    handlers.setup(dp)

    await set_commands(bot, config, sessionmaker)
    await schedule.setup(bot, sessionmaker)
    bot_info = await bot.me()

    try:

        await dp.start_polling(
            bot,
            config=config,
            bot_info=bot_info,
            payment=payment,
        )

    finally:

        await dp.fsm.storage.close()


try:

    asyncio.run(main())

except (
    KeyboardInterrupt,
    SystemExit,
):

    log.critical("Bot stopped")
