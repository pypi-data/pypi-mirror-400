import asyncio
from dataclasses import dataclass
import json
import logging

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class CattleGridApi:
    domain: str
    username: str
    password: str
    token: str | None = None

    async def _signin(self, session: aiohttp.ClientSession):
        response = await session.post(
            f"http://{self.domain}/fe/signin",
            json={"name": self.username, "password": self.password},
        )
        data = await response.json()
        logger.info(data)

        self.token = data.get("token")
        await asyncio.sleep(0.2)

    async def public_posts(self, session: aiohttp.ClientSession):
        if not self.token:
            await self._signin(session)
        response = await session.get(
            f"http://{self.domain}/fe/account/history",
            params={"start_from": "019b0482-2dbd-7604-ad1e-d21ded5e8912"},
            headers={"authorization": f"Bearer {self.token}"},
        )
        data = await response.json()

        logger.debug(json.dumps(data, indent=2))

        return data.get("events")
