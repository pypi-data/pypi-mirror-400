from dataclasses import dataclass

import aiohttp
from .api import MastodonApi


@dataclass
class MastodonObjectGetter:
    domain: str
    token: str = "token"
    api: MastodonApi = None  # type: ignore

    def __post_init__(self):
        self.api = MastodonApi(self.domain, self.token)

    async def fetch_object(self, session: aiohttp.ClientSession, object_id: str):
        public_posts = await self.api.public_posts(session)

        for x in public_posts:
            if x.get("uri") == object_id:
                return x

        return None
