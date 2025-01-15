"""Queue model"""
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import bigint, Base
from .user import User


class Queue(Base):
    """Queue model"""
    __tablename__ = 'queue'

    id: Mapped[bigint] = mapped_column(ForeignKey(User.id), primary_key=True)
    is_man: Mapped[bool]
    target_man: Mapped[Optional[bool]]
    is_adult: Mapped[bool]

    user: Mapped["User"] = relationship()
