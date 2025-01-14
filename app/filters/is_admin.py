"""Is admin filter"""
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from app.database.models import User
from app.utils.config import Settings


class IsAdmin(Filter):
    """Check if user is an admin"""

    def __init__(self, is_admin: bool = True) -> None:
        """Initialize the IsAdmin filter"""
        self.is_admin = is_admin

    async def __call__(
        self,
        update: Message | CallbackQuery,
        config: Settings,
        user: User,
    ) -> bool:
        """Check if user is an admin"""
        return self.is_admin == (
            update.from_user.id
            in config.bot.admins
            or user.is_admin
        )
