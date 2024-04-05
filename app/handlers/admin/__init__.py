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

from aiogram import Router


def setup(router: Router):
    """
    Register admin handlers.

    :param Router router: Admin Router
    """
    
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
