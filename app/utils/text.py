from typing import Optional
from aiogram import types


def escape(text: str) -> str:
    """
    Escape text for HTML parse mode

    :param str text: Input text
    :return str: Escaped text
    """
    
    return (
        text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
    )


def link(user: types.User, text: str | None=None) -> str:
    """
    Generate direct link

    :param types.User user: AIOGram user object
    :param str | None text: Link text, defaults to user's first name
    :return str: Direct link as href
    """
    
    url = (
        'https://t.me/%s' % user.username
        if user.username else
        'tg://user?id=%i' % user.id
    )
    
    return '<a href="%s">%s</a>' % (
        url, text or escape(user.first_name),
    )


def get_ref(message: types.Message, check: bool=True) -> Optional[str]:
    """
    Get reflink of a message. If check is True, it will check if the message is a /start command.

    :param types.Message message: AIOGram message object
    :param bool check: Check if the message is a /start command
    :return Optional[str]: Ref link or None
    """

    if check and not message.text.startswith('/start'):

        return

    if args := message.text.split()[1:]:
        
        return args[0]
