import aiohttp
from dataclasses import dataclass

from .api import MastodonApi
from funfedi_connect.types import (
    ApplicationConfiguration,
    ApplicationPoster,
    ImplementedFeature,
    ParsingTestApplicationConfiguration,
)

from .object_getter_class import MastodonObjectGetter


@dataclass
class MastodonApplication(ApplicationConfiguration):
    domain: str
    username: str
    application_name: str = "mastodon"
    features = [
        ImplementedFeature.webfinger,
        ImplementedFeature.public_timeline,
        ImplementedFeature.post,
    ]

    async def build_object_parsing(
        self, session: aiohttp.ClientSession
    ) -> ParsingTestApplicationConfiguration:
        actor_uri = await self._determine_actor_uri(session)

        if actor_uri is None:
            raise ValueError("failed to determine actor")

        object_getter = MastodonObjectGetter(self.domain)

        return ParsingTestApplicationConfiguration(
            actor_id=actor_uri,
            application_name=self.application_name,
            base_object_getter=object_getter.fetch_object,
        )

    async def build_poster(self, session: aiohttp.ClientSession) -> ApplicationPoster:
        api = MastodonApi(self.domain, "token")

        return api.post
