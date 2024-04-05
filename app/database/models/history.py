from . import Base
from .base import bigint

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[bigint]
    ad_id: Mapped[int] 
    time: Mapped[datetime] = mapped_column(default=datetime.now)
