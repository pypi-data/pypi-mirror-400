from dataclasses import dataclass, field

import aiohttp


@dataclass
class GancioEventRetriever:
    domain: str
    login: str
    password: str
    token: str | None = field(default=None)

    @property
    def _login_data(self):
        return {
            "username": self.login,
            "password": self.password,
            "grant_type": "password",
            "client_id": "self",
        }

    async def init_token(self, session):
        async with session.post(
            f"http://{self.domain}/oauth/login", data=self._login_data
        ) as response:
            data = await response.json()
            self.token = data.get("access_token")

            if self.token is None:
                raise Exception("Failed to fetch token")

        async with session.post(
            f"http://{self.domain}/api/ap_actors/add_trust",
            json={"url": "http://pasture-one-actor/actor"},
            headers={"authorization": f"Bearer {self.token}"},
        ) as resp:
            assert resp.status == 200

    async def fetch_event(self, session: aiohttp.ClientSession, object_id: str):
        async with session.get(f"http://{self.domain}/api/events") as response:
            events = await response.json()
            for event in events:
                slug = event.get("slug")
                if slug:
                    details = await self.event_details(session, slug)
                    if details.get("original_url") == object_id:
                        return details

    async def event_details(self, session: aiohttp.ClientSession, slug: str):
        async with session.get(
            f"http://{self.domain}/api/event/detail/{slug}"
        ) as response:
            return await response.json()
