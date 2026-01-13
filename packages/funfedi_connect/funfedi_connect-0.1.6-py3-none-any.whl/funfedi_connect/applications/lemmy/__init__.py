import aiohttp
from dataclasses import dataclass

from .object_getter_class import LemmyObjectGetter
from funfedi_connect.types import (
    ApplicationConfiguration,
    ImplementedFeature,
    ParsingTestApplicationConfiguration,
)


@dataclass
class LemmyApplication(ApplicationConfiguration):
    domain: str
    username: str
    application_name: str = "lemmy"
    features = [ImplementedFeature.webfinger, ImplementedFeature.public_timeline]

    async def build_object_parsing(
        self, session: aiohttp.ClientSession
    ) -> ParsingTestApplicationConfiguration:
        actor_uri = await self._determine_actor_uri(session)

        if actor_uri is None:
            raise ValueError("failed to determine actor")

        object_getter = LemmyObjectGetter(self.domain)

        return ParsingTestApplicationConfiguration(
            actor_id=actor_uri,
            application_name=self.application_name,
            base_object_getter=object_getter.fetch_object,
        )
