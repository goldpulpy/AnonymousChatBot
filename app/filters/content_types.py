"""Content types filter"""
from aiogram.filters import Filter
from aiogram.types import Message, ContentType


class ContentTypes(Filter):
    """
    Legacy-like content-types filter
    """

    def __init__(self, *content_types: str):
        """
        Initialize the ContentTypes filter
        """
        self.content_types = content_types

    async def __call__(self, update: Message) -> bool:
        """
        Check if the message content type is in the allowed list
        """
        return (
            (update.content_type in self.content_types)
            or (ContentType.ANY in self.content_types)
        )
