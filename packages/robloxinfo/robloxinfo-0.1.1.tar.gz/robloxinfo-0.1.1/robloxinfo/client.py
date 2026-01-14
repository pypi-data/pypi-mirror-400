import requests
from datetime import datetime
from .models import RobloxUser
from .exceptions import RobloxAPIError, UserNotFound


class RobloxClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {"User-Agent": "robloxinfo/1.0"}

    def get_user(self, username: str) -> RobloxUser:
        # Username -> ID
        r = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": False},
            headers=self.headers,
            timeout=self.timeout
        )

        if r.status_code != 200:
            raise RobloxAPIError("Username lookup failed")

        data = r.json()["data"]
        if not data:
            raise UserNotFound(username)

        user_id = data[0]["id"]

        # User details
        user = requests.get(
            f"https://users.roblox.com/v1/users/{user_id}",
            headers=self.headers,
            timeout=self.timeout
        ).json()

        created = datetime.fromisoformat(
            user["created"].replace("Z", "")
        )

        # Social counts
        friends = requests.get(
            f"https://friends.roblox.com/v1/users/{user_id}/friends/count",
            headers=self.headers,
            timeout=self.timeout
        ).json()["count"]

        followers = requests.get(
            f"https://friends.roblox.com/v1/users/{user_id}/followers/count",
            headers=self.headers,
            timeout=self.timeout
        ).json()["count"]

        following = requests.get(
            f"https://friends.roblox.com/v1/users/{user_id}/followings/count",
            headers=self.headers,
            timeout=self.timeout
        ).json()["count"]

        # Avatar
        avatar = requests.get(
            "https://thumbnails.roblox.com/v1/users/avatar",
            params={
                "userIds": user_id,
                "size": "420x420",
                "format": "Png",
                "isCircular": False
            },
            headers=self.headers,
            timeout=self.timeout
        ).json()["data"][0]["imageUrl"]

        # Presence
        presence_data = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            json={"userIds": [user_id]},
            headers=self.headers,
            timeout=self.timeout
        ).json()["userPresences"][0]

        status_map = {
            0: "Offline",
            1: "Online",
            2: "In Game",
            3: "In Studio"
        }

        presence = status_map.get(
            presence_data.get("userPresenceType"), "Unknown"
        )

        last_online = presence_data.get("lastOnline")

        return RobloxUser(
            id=user_id,
            username=user["name"],
            display_name=user["displayName"],
            description=user["description"],
            created=created,
            is_banned=user["isBanned"],
            friends=friends,
            followers=followers,
            following=following,
            presence=presence,
            last_online=last_online,
            avatar_url=avatar
        )
