from dataclasses import dataclass

import aiohttp


@dataclass
class MisskeyApi:
    domain: str

    misskey_i_token: str = "token"

    async def users_on_domain(self, session: aiohttp.ClientSession):
        response = await session.post(
            f"http://{self.domain}/api/users/search",
            json={"query": "actor", "i": self.misskey_i_token},
            headers={"content-type": "application/json"},
        )
        return await response.json()

    async def misskey_user_id_for_actor_uri(
        self, session: aiohttp.ClientSession, actor_uri: str
    ) -> str:
        result = await self.users_on_domain(session)
        for x in result:
            if x.get("uri") == actor_uri:
                return x.get("id")
        raise ValueError("Actor not found in Misskey response")

    async def public_posts_for_user_id(
        self, session: aiohttp.ClientSession, user_id: str
    ):
        response = await session.post(
            "http://misskey/api/users/notes",
            json={"userId": user_id, "i": self.misskey_i_token},
            headers={"Authorization": "Bearer token"},
        )
        return await response.json()
