"""Not subbed filter"""
from aiogram.filters import Filter


class NotSubbed(Filter):
    """Check if user is subbed"""

    def __init__(self) -> None:
        """Initialize the NotSubbed filter"""
        pass

    async def __call__(self, _, sponsors: list) -> bool:
        """Check if user is subbed"""
        return bool(sponsors)
