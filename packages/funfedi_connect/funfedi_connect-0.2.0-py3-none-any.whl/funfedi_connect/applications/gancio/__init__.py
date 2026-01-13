import aiohttp
from dataclasses import dataclass

from .event_retriever import GancioEventRetriever
from funfedi_connect.types import (
    ApplicationConfiguration,
    ImplementedFeature,
)
from ...types.parsing import ParsingTestApplicationConfiguration


@dataclass
class GancioApplication(ApplicationConfiguration):
    domain: str
    username: str
    login: str = "g@gancio.io"
    password: str = "password"
    application_name: str = "gancio"
    features = [ImplementedFeature.webfinger, ImplementedFeature.event]

    async def build_event_parsing(
        self, session: aiohttp.ClientSession
    ) -> ParsingTestApplicationConfiguration:
        actor_uri = await self._determine_actor_uri(session)

        if actor_uri is None:
            raise ValueError("failed to determine actor")

        event_retriever = GancioEventRetriever(
            self.domain,
            self.login,
            self.password,
        )

        await event_retriever.init_token(session)

        return ParsingTestApplicationConfiguration(
            actor_id=actor_uri,
            application_name=self.application_name,
            base_object_getter=event_retriever.fetch_event,
        )
