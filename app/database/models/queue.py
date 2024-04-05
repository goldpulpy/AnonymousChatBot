from . import Base
from .base import bigint
from .user import User

from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Queue(Base):
    __tablename__ = 'queue'

    id: Mapped[bigint] = mapped_column(ForeignKey(User.id), primary_key=True)
    is_man: Mapped[bool]
    target_man: Mapped[Optional[bool]]
    is_adult: Mapped[bool]

    user: Mapped["User"] = relationship()
