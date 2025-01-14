"""Is registered filter"""
from aiogram.filters import Filter
from app.database.models import User


class IsRegistered(Filter):
    """Check if user is Registered"""

    def __init__(self, is_registered: bool = True) -> None:
        """Initialize the IsRegistered filter"""
        self.is_registered = is_registered

    async def __call__(self, _, user: User) -> bool:
        """Check if user is registered"""
        return self.is_registered == (user.is_man is not None)
