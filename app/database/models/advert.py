"""Advert model"""
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from . import Base


class Advert(Base):
    """Advert model"""
    __tablename__ = 'adverts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    type: Mapped[int]
    title: Mapped[str]
    text: Mapped[str]
    file_id: Mapped[Optional[str]]
    markup: Mapped[Optional[str]]

    views: Mapped[int] = mapped_column(default=0)
    target: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
