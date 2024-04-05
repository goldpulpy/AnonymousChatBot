from app.database.models import User

from aiogram.filters import Filter


class IsRegistered(Filter):
    """
    Check if user is Registered
    """

    def __init__(self, is_registered: bool=True):

        self.is_registered = is_registered

    async def __call__(self, _, user: User) -> bool:

        return self.is_registered == (user.is_man is not None)
