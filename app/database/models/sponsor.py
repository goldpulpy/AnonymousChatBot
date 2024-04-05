from . import Base

from sqlalchemy.orm import Mapped, mapped_column


class Sponsor(Base):
    __tablename__ = 'sponsors'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    check: Mapped[bool] = mapped_column(default=False)
    is_bot: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    title: Mapped[str]
    link: Mapped[str]
    access_id: Mapped[str]

    visits: Mapped[int] = mapped_column(default=0)
    limit: Mapped[int] = mapped_column(default=0)
