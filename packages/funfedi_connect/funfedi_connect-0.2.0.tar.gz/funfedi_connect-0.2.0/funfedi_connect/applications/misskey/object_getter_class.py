import asyncio
from dataclasses import dataclass

import aiohttp

from .api import MisskeyApi


@dataclass
class MisskeyObjectGetter:
    domain: str
    api: MisskeyApi = None  # type: ignore
    remote_actor_uri: str = "http://pasture-one-actor/actor"
    user_id: str | None = None

    def __post_init__(self):
        self.api = MisskeyApi(self.domain)

    async def fetch_object(self, session: aiohttp.ClientSession, object_id: str):
        if self.user_id is None:
            await asyncio.sleep(1)
            self.user_id = await self.api.misskey_user_id_for_actor_uri(
                session, self.remote_actor_uri
            )

        public_posts = await self.api.public_posts_for_user_id(session, self.user_id)

        for x in public_posts:
            if x.get("uri") == object_id:
                return x

        return None
