from . import Base
from .base import bigint

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Dialogue(Base):
    __tablename__ = 'dialogues'

    first: Mapped[bigint] = mapped_column(ForeignKey('users.id'), primary_key=True)
    second: Mapped[bigint] = mapped_column(ForeignKey('users.id'), primary_key=True)

    def get_id(self, first: int) -> int:

        return self.first if first == self.second else self.second
