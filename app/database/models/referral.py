"""Referral model"""
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from . import Base


class Referral(Base):
    """Referral model"""
    __tablename__ = 'referrals'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    ref: Mapped[str]
    total: Mapped[int] = mapped_column(default=0)
    price: Mapped[Optional[int]]
