from aiogram.filters import Filter

class NotSubbed(Filter):
    """
    Check if user is subbed
    """
    def __init__(self):
        pass

    
    async def __call__(self,_, sponsors: list) -> bool:

        return bool(sponsors)
