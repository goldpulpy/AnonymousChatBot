"""Is vip filter"""
from aiogram.filters import Filter
from app.database.models import User


class IsVip(Filter):
    """Check if user is VIP"""

    def __init__(self, is_vip: bool = True) -> None:
        """Initialize the IsVip filter"""
        self.is_vip = is_vip

    async def __call__(self, _, user: User) -> bool:
        """Check if user is VIP"""
        return self.is_vip == user.is_vip
