"""Room model"""
import random
import json
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON
from room_nicknames import MAN, FEMALE
from . import Base


class Room(Base):
    """Room model"""
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    room_name: Mapped[str] = mapped_column(default=None)
    room_online_members: Mapped[int] = mapped_column(default=0)
    room_online_limit: Mapped[int] = mapped_column(default=0)
    room_members: Mapped[List[Optional[str]]] = mapped_column(
        type_=JSON, default=[]
    )

    @property
    def room_members_list(self):
        if self.room_members:
            return json.loads(self.room_members)
        return []

    def join_room(self, user_id: int, is_man: bool) -> str:
        members = self.room_members_list if self.room_members else []
        for member in members:
            if member.get("user_id") == user_id:
                member["status"] = "online"
                self.room_members = json.dumps(members)
                return member.get("nickname")

        while True:
            nickname = self.generate_nickname(is_man)
            for member in members:
                if member.get("nickname") == nickname:
                    continue
            break

        members.append(
            {"user_id": user_id, "nickname": nickname, "status": "online"}
        )

        self.room_members = json.dumps(members)
        return nickname

    def generate_nickname(self, is_man: bool) -> str:
        """Generate nickname"""
        if is_man:
            return random.choice(MAN)
        return random.choice(FEMALE)

    def leave_room(self, user_id: int):
        """Leave room"""
        members = self.room_members_list if self.room_members else []
        for member in members:
            if member.get("user_id") == user_id:
                member["status"] = "offline"
                self.room_members = json.dumps(members)

    def get_online_members(self) -> List[str]:
        """Get online members"""
        members = self.room_members_list if self.room_members else []
        return [
            member.get("user_id")
            for member in members if member.get("status") == "online"
        ]

    def get_online_members_nickname(self) -> List[str]:
        """Get online members nickname"""
        members = self.room_members_list if self.room_members else []

        return [
            member.get("nickname")
            for member in members if member.get("status") == "online"
        ]

    def get_nickname(self, user_id: int) -> Optional[str]:
        """Get nickname"""
        members = self.room_members_list if self.room_members else []

        for member in members:
            if member.get("user_id") == user_id:
                return member.get("nickname")
        return None

    def change_nickname(self, user_id: int, nickname: str) -> None:
        members = self.room_members_list if self.room_members else []
        for member in members:
            if member.get("user_id") == user_id:
                member["nickname"] = nickname
                self.room_members = json.dumps(members)
