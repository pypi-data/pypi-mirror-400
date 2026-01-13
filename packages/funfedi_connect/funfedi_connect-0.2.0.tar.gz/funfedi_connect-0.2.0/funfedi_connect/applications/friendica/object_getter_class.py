from dataclasses import dataclass

import aiohttp
from .api import FriendicaApi


@dataclass
class FriendicaObjectGetter:
    domain: str
    username: str
    password: str
    api: FriendicaApi = None  # type: ignore

    def __post_init__(self):
        self.api = FriendicaApi(self.domain, self.username, self.password)

    async def fetch_object(self, session: aiohttp.ClientSession, object_id: str):
        public_posts = await self.api.public_posts(session)

        for x in public_posts:
            if x.get("uri") == object_id:
                return x

        return None
