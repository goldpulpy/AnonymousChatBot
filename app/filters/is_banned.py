"""Is banned filter"""
from aiogram.filters import Filter
from app.database.models import User


class IsBanned(Filter):
    """Check if user is banned"""

    def __init__(self, is_banned: bool = False) -> None:
        """Initialize the IsBanned filter"""
        self.is_banned = is_banned

    async def __call__(self, _, user: User) -> bool:
        """Check if user is banned"""
        return self.is_banned == user.is_banned
