from app.database.models import User

from aiogram.filters import Filter


class InDialogue(Filter):

    def __init__(self, in_dialogue: bool=True):

        self.in_dialogue = in_dialogue

    async def __call__(self, _, user: User):

        return (user.partner is not None) == self.in_dialogue
