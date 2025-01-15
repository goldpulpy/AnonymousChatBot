"""Dialogue model"""
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import bigint, Base


class Dialogue(Base):
    """Dialogue model"""
    __tablename__ = 'dialogues'

    first: Mapped[bigint] = mapped_column(
        ForeignKey('users.id'), primary_key=True
    )
    second: Mapped[bigint] = mapped_column(
        ForeignKey('users.id'), primary_key=True
    )

    def get_id(self, first: int) -> int:
        """Get user in dialogue id"""
        return self.first if first == self.second else self.second
