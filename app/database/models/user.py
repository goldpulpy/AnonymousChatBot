"""User model"""
import json
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON
from .base import bigint, Base
from .dialogue import Dialogue


class User(Base):
    __tablename__ = 'users'

    id: Mapped[bigint] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[Optional[str]] = mapped_column(default=None)
    first_name: Mapped[Optional[str]] = mapped_column(default=None)
    last_name: Mapped[Optional[str]] = mapped_column(default=None)

    join_date: Mapped[datetime] = mapped_column(default=datetime.now)
    block_date: Mapped[Optional[datetime]]

    ref: Mapped[Optional[str]]
    subbed: Mapped[bool] = mapped_column(default=False)
    subbed_before: Mapped[bool] = mapped_column(default=False)

    invited: Mapped[int] = mapped_column(default=0)
    age: Mapped[Optional[int]]
    is_man: Mapped[Optional[bool]]

    vip_time: Mapped[datetime] = mapped_column(
        default=datetime.fromtimestamp(0)
    )
    balance: Mapped[int] = mapped_column(default=0)
    chat_only: Mapped[bool] = mapped_column(default=False)

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    friends: Mapped[List[Optional[str]]] = mapped_column(
        type_=JSON, default=[])

    in_room: Mapped[int] = mapped_column(default=0)

    dialogue_id: Mapped[bigint] = mapped_column(nullable=True)

    partner: Mapped[Optional["Dialogue"]] = relationship(
        primaryjoin="or_("
        "    User.id==Dialogue.first,"
        "    User.id==Dialogue.second,"
        ")",
    )

    @property
    def friends_list(self):
        if self.friends:
            return json.loads(self.friends)
        return []

    def is_friend(self, friend_id: int) -> bool:
        current_friends = self.friends_list if self.friends else []
        if friend_id in current_friends:
            return True
        return False

    def add_friend(self, friend_id: int) -> None:
        current_friends = self.friends_list if self.friends else []

        if friend_id not in current_friends:
            current_friends.append(friend_id)

        self.friends = json.dumps(current_friends)

    def remove_friend(self, friend_id: int) -> None:

        current_friends = self.friends_list if self.friends else []

        if friend_id in current_friends:
            current_friends.remove(friend_id)

        self.friends = json.dumps(current_friends)

    @property
    def partner_id(self) -> int:
        return self.partner.get_id(self.id)

    @property
    def is_vip(self) -> bool:
        return (
            self.vip_time is not None
            and self.vip_time > datetime.now()
        )

    def add_vip(self, days: int) -> None:
        """
        Add VIP days to user. You need to commit after.

        :param int days: Amount of days
        """

        self.vip_time = max(
            self.vip_time, datetime.now()
        ) + timedelta(days=days)
