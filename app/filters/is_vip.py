from app.database.models import User

from aiogram.filters import Filter


class IsVip(Filter):
    """
    Check if user is VIP
    """

    def __init__(self, is_vip: bool=True):

        self.is_vip = is_vip

    async def __call__(self, _, user: User) -> bool:

        return self.is_vip == user.is_vip
