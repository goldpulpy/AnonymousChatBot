"""In room filter"""
from aiogram.filters import Filter
from app.database.models import User


class InRoom(Filter):
    """Check if the user is in a room"""

    def __init__(self, in_room: bool = True) -> None:
        """Initialize the InRoom filter"""
        self.in_room = in_room

    async def __call__(self, _, user: User) -> bool:
        """Check if the user is in a room"""
        return (user.in_room != 0) == self.in_room
