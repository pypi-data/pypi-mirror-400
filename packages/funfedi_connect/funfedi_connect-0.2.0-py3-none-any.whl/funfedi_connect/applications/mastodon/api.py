from dataclasses import dataclass
import json
import logging

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class MastodonApi:
    domain: str
    token: str

    @property
    def headers(self) -> dict:
        return {"authorization": f"Bearer {self.token}"}

    async def public_posts(self, session: aiohttp.ClientSession):
        response = await session.get(
            f"http://{self.domain}/api/v1/timelines/public",
            headers=self.headers,
        )
        data = await response.json()

        logger.debug(json.dumps(data, indent=2))

        return data

    async def post(self, session: aiohttp.ClientSession, content):
        response = await session.post(
            f"http://{self.domain}/api/v1/statuses",
            headers=self.headers,
            json={"status": content},
        )
        if response.status != 200:
            print(response)
            print(await response.text())
            raise Exception("Failed to post")

        data = await response.json()

        return data.get("uri")
