"""Request model"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
from .base import bigint


class Request(Base):
    """Request model"""
    __tablename__ = 'requests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[bigint]
    chat_id: Mapped[bigint]
    time: Mapped[datetime]
