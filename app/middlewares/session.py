from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from sqlalchemy.ext.asyncio import async_sessionmaker


class SessionMiddleware(BaseMiddleware):
    """
    Middleware for adding session.
    """

    def __init__(self, sessionmaker: async_sessionmaker):

        self.sessionmaker = sessionmaker


    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
    
        async with self.sessionmaker() as session:

            data["session"] = session
            return await handler(event, data)