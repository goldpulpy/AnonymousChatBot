from . import (
    start,
    notsubbed,
    events,
    vip, 
    profile,
    dialogue,
    banned,
    myfriends,
    rooms
)
from aiogram import Router, Dispatcher


def setup(dp: Dispatcher, router: Router):
    """
    Register user handlers.

    :param Dispatcher dp: Dispatcher (root Router), needed for events
    :param Router router: User Router
    """
    
    events.register(dp)
    
    banned.register(router)
    start.register(router)
    vip.register(router)

    # all handlers afther `notsubbed` will work after user subscribed.
    notsubbed.register(router)

    rooms.register(router)
    profile.register(router)
    myfriends.register(router)
    dialogue.register(router)
