"""Banned handlers"""
from aiogram import Router, types
from app.filters import IsBanned
from app.templates import texts


async def user_banned(message: types.Message) -> None:
    """User banned handler"""
    await message.answer(texts.user.BANNED)


def register(router: Router) -> None:
    """Register banned handler"""
    router.message.register(user_banned, IsBanned(True))
