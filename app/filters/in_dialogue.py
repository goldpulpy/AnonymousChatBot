"""In dialogue filter"""
from aiogram.filters import Filter
from app.database.models import User


class InDialogue(Filter):
    """Check if the user is in a dialogue"""

    def __init__(self, in_dialogue: bool = True) -> None:
        """Initialize the InDialogue filter"""
        self.in_dialogue = in_dialogue

    async def __call__(self, _, user: User) -> bool:
        """Check if the user is in a dialogue"""
        return (user.partner is not None) == self.in_dialogue
