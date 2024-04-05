import time
import asyncio

from typing import Optional
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter


class MailerSingleton(object):

    DEFAULT_DELAY = 1/25
    __instance = None


    def __init__(self, delay: int | float=None) -> None:
        """
        Creator of MailerSingleton. Raises an exception if an instance already exists.

        :param int | float delay: Delay between messages, optional.
        :raises Exception: If an instance already exists.
        """

        if MailerSingleton.__instance is not None:

            raise Exception('MailingSingleton is a singleton!')

        self.delay = delay or self.DEFAULT_DELAY
        MailerSingleton.__instance = self


    @staticmethod
    def get_instance() -> 'MailerSingleton':
        """
        Get an instance of MailerSingleton.

        :return MailerSingleton: Already existing / newly created instance.
        """

        if MailerSingleton.__instance is None:

            MailerSingleton()

        return MailerSingleton.__instance


    @staticmethod
    def pretty_time(seconds: float) -> str:
        """
        Get a pretty time string.

        :param float seconds: UNIX timestamp.
        :return str: Time in hunan-readable format.
        """

        seconds = int(seconds)

        return '%0d:%0d:%0d' % (
            seconds // 3600,
            seconds % 3600 // 60,
            seconds % 60
        )


    @classmethod
    def get_text(cls, scope: list[int], sent: int, delay: float) -> str:
        """
        Get an ETA message.

        :param list[int] scope: Scope of users.
        :param int sent: Progress of mailing.
        :param float delay: Delay between messages.
        :return str: Ready message.
        """

        progress = int(sent / len(scope) * 25)
        progress_bar = ('=' * progress) + (' ' * (25 - progress))

        return "<code>[%s]</code> %s/%s (ETA: %s)" % (
            progress_bar,
            sent,
            len(scope),
            cls.pretty_time((len(scope) - sent) * delay)
        )


    async def start_mailing(
        self, 
        message_id: int, 
        reply_markup: Optional[dict], 
        chat_id: int, 
        bot: Bot, 
        scope: list[int], 
        cancel_keyboard: dict
    ):
        """
        Start mailing.

        :param int message_id: Target message ID.
        :param Optional[dict] reply_markup: Target message reply markup.
        :param int chat_id: Target chat ID.
        :param Bot bot: An instance of Bot.
        :param list[int] scope: Users to send to.
        :param dict cancel_keyboard: Cancel keyboard.
        """

        self.TIME_STARTED = time.monotonic()

        time_started = self.TIME_STARTED
        blocked = 0
        delay = self.delay

        message = await bot.send_message(
            chat_id,
            self.get_text(scope, 1, delay),
            reply_markup=cancel_keyboard,
        )
        self.last_update = time.monotonic()

        for sent, user_id in enumerate(scope, 1):

            if self.TIME_STARTED != time_started:

                break

            if time.monotonic() - self.last_update > 2:

                self.last_update = time.monotonic()

                with suppress(TelegramAPIError):
                    
                    await message.edit_text(
                        self.get_text(
                            scope, sent, delay,
                        ),
                        reply_markup=cancel_keyboard,
                    )

            try:

                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup,
                )

            except TelegramRetryAfter as exc:

                delay *= 2
                await asyncio.sleep(exc.retry_after)

            except TelegramAPIError:

                blocked += 1

            await asyncio.sleep(delay)

        with suppress(TelegramAPIError):

            await message.edit_text(
                self.get_text(
                    scope, len(scope), delay,
                ),
            )

        await message.answer(
            'Рассылка завершена. Успешно: %s. Бот заблокирован: %s' % (
                (len(scope) - blocked), blocked,
            ),
        )


    def stop_mailing(self) -> bool:
        """
        Stops mailing. Returns True on success.

        :return bool: True on successful stop.
        """

        if self.TIME_STARTED == 0:

            return False

        self.TIME_STARTED = 0

        return True


    @property
    def is_mailing(self) -> bool:
        """
        Check if mailing is in progress.

        :return bool: True if mailing is in progress.
        """

        return self.TIME_STARTED != 0
