"""Request channel model"""
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
from .base import bigint


class RequestChannel(Base):
    """Request channel model"""
    __tablename__ = 'request_channels'

    id: Mapped[bigint] = mapped_column(primary_key=True, autoincrement=True)

    active: Mapped[bool] = mapped_column(default=False)
    title: Mapped[str]
    visits: Mapped[int] = mapped_column(default=0)
