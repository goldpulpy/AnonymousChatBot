"""Dialogue history model"""
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from . import Base
from .base import bigint


class DialogueHistory(Base):
    """Dialogue history model"""
    __tablename__ = 'dialogues_history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dialogue_id: Mapped[bigint]
    first: Mapped[bigint] = mapped_column(ForeignKey('users.id'))
    second: Mapped[bigint] = mapped_column(ForeignKey('users.id'))
    time: Mapped[datetime] = mapped_column(default=datetime.now)
    message: Mapped[str]
    image_id: Mapped[Optional[str]] = mapped_column(default=None)
