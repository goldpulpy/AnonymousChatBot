from app.database.models import User

from aiogram.filters import Filter


class InRoom(Filter):

    def __init__(self, in_room: bool=True):

        self.in_room = in_room

    async def __call__(self, _, user: User):

        return (user.in_room != 0) == self.in_room