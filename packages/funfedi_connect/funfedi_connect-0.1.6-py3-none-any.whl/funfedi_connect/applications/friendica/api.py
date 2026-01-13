from dataclasses import dataclass
import json
import logging

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class FriendicaApi:
    domain: str
    username: str
    password: str

    @property
    def host(self):
        return f"{self.username}:{self.password}@{self.domain}"

    async def public_posts(self, session: aiohttp.ClientSession):
        response = await session.get(
            f"http://{self.host}/api/v1/timelines/public",
        )
        data = await response.json()

        logger.debug(json.dumps(data, indent=2))

        return data

    async def post(self, session: aiohttp.ClientSession, content):
        response = await session.post(
            f"http://{self.host}/api/v1/statuses",
            json={"status": content},
        )
        if response.status != 200:
            print(
                f"http://{self.host}/api/v1/statuses",
            )
            print(response)
            print(await response.text())
            raise Exception("Failed to post")

        data = await response.json()

        return data.get("uri")
