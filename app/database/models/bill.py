from . import Base
from .base import bigint

from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class Bill(Base):
    __tablename__ = 'bills'

    id: Mapped[bigint] = mapped_column(primary_key=True)

    user_id: Mapped[bigint]

    amount: Mapped[int]
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    ref: Mapped[Optional[str]]
