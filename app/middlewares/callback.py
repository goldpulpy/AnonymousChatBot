from contextlib import suppress
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, exceptions
from aiogram.types import CallbackQuery, Update


class CallbackMiddleware(BaseMiddleware):
    """
    Middleware for answering untouched callback queries.
    """

    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        call: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
    
        await handler(call, data)

        with suppress(exceptions.TelegramAPIError):

            await call.answer()
