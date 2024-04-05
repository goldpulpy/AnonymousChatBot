from . import Base
from .base import bigint

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional,List
from sqlalchemy import Column, String, ARRAY, JSON

from room_nicknames import MAN, FEMALE
import random, json


class Room(Base):
    __tablename__ = 'rooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    room_name: Mapped[str] = mapped_column(default=None)
    room_online_members: Mapped[int] = mapped_column(default=0)
    room_online_limit: Mapped[int] = mapped_column(default=0)
    room_members: Mapped[List[Optional[str]]] = mapped_column(type_=JSON, default=[])


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

            nickname = self.generate_nickname(user_id, is_man)

            for member in members:

                if member.get("nickname") == nickname:

                    continue

            break


        members.append({"user_id": user_id, "nickname": nickname, "status": "online"})

        self.room_members = json.dumps(members)

        return nickname

    def generate_nickname(self, user_id: int, is_man: bool) -> str:
        
        if is_man:

            return random.choice(MAN)

        return random.choice(FEMALE)


    def leave_room(self, user_id: int):

        members = self.room_members_list if self.room_members else []

        for member in members:

            if member.get("user_id") == user_id:

                member["status"] = "offline"

                self.room_members = json.dumps(members)


    def get_online_members(self) -> List[str]:

        members = self.room_members_list if self.room_members else []

        return [member.get("user_id") for member in members if member.get("status") == "online"]

    def get_online_members_nickname(self) -> List[str]:

        members = self.room_members_list if self.room_members else []

        return [member.get("nickname") for member in members if member.get("status") == "online"]

    def get_nickname(self, user_id: int) -> Optional[str]:

        members = self.room_members_list if self.room_members else []

        for member in members:

            if member.get("user_id") == user_id:

                return member.get("nickname")

        return None

    def change_nickname(self, user_id: int, nickname: str):

        members = self.room_members_list if self.room_members else []

        for member in members:

            if member.get("user_id") == user_id:

                member["nickname"] = nickname

                self.room_members = json.dumps(members)