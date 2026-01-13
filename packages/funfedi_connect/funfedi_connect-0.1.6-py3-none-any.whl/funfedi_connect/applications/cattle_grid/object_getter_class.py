from dataclasses import dataclass
import logging

import aiohttp
from .api import CattleGridApi


logger = logging.getLogger(__name__)


@dataclass
class CattleGridObjectGetter:
    domain: str
    username: str = "cow"
    password: str = "pass"
    api: CattleGridApi = None  # type: ignore

    def __post_init__(self):
        self.api = CattleGridApi(
            self.domain, username=self.username, password=self.password
        )

    async def fetch_object(self, session: aiohttp.ClientSession, object_id: str):
        public_posts = await self.api.public_posts(session)

        for x in public_posts:
            parsed = x.get("data").get("parsed")
            obj = parsed.get("embedded_object")
            if obj.get("id") == object_id:
                return x

        return None
