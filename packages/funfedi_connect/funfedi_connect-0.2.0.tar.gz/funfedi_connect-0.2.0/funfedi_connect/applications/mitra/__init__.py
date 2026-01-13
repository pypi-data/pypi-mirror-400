from dataclasses import dataclass

import aiohttp

from ..mastodon.api import MastodonApi
from funfedi_connect.applications.mastodon.object_getter_class import (
    MastodonObjectGetter,
)
from funfedi_connect.types import (
    ApplicationConfiguration,
    ApplicationPoster,
    ImplementedFeature,
    ParsingTestApplicationConfiguration,
)


@dataclass
class MitraApplication(ApplicationConfiguration):
    domain: str
    username: str
    application_name: str = "mitra"
    password: str = "password"

    features = [
        ImplementedFeature.webfinger,
        ImplementedFeature.public_timeline,
        ImplementedFeature.post,
    ]

    async def _determine_token(self, session: aiohttp.ClientSession):
        async with session.post(
            f"http://{self.domain}/oauth/token",
            data={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            },
        ) as response:
            data = await response.json()

        return data["access_token"]

    async def build_object_parsing(
        self, session: aiohttp.ClientSession
    ) -> ParsingTestApplicationConfiguration:
        actor_uri = await self._determine_actor_uri(session)

        if actor_uri is None:
            raise ValueError("failed to determine actor")

        token = await self._determine_token(session)

        object_getter = MastodonObjectGetter(self.domain, token=token)

        return ParsingTestApplicationConfiguration(
            actor_id=actor_uri,
            application_name=self.application_name,
            base_object_getter=object_getter.fetch_object,
        )

    async def build_poster(self, session: aiohttp.ClientSession) -> ApplicationPoster:
        token = await self._determine_token(session)
        api = MastodonApi(self.domain, token)

        return api.post
