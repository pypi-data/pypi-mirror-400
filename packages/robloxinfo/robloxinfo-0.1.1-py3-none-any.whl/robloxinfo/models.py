from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RobloxUser:
    id: int
    username: str
    display_name: str
    description: str
    created: datetime
    is_banned: bool
    friends: int
    followers: int
    following: int
    presence: str
    last_online: Optional[str]
    avatar_url: str
