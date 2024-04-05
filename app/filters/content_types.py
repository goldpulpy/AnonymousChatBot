from aiogram.filters import Filter
from aiogram.types import Message, ContentType


class ContentTypes(Filter):
    """
    Legacy-like content-types filter
    """

    def __init__(self, *content_types: str):

        self.content_types = content_types

    async def __call__(self, update: Message) -> bool:

        return (
            (update.content_type in self.content_types) 
            or (ContentType.ANY in self.content_types)
        )
