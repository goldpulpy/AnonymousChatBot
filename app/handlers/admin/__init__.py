"""Admin handlers"""
from aiogram import Router
from . import (
    dump,
    start,
    commands,
    stats,
    referrals,
    subscribe,
    mail,
    adverts,
    requests,
    rooms,
)


def setup(router: Router) -> None:
    """Register admin handlers"""
    start.register(router)
    commands.register(router)
    dump.register(router)
    mail.register(router)
    stats.register(router)
    referrals.register(router)
    subscribe.register(router)
    adverts.register(router)
    requests.register(router)
    rooms.register(router)
