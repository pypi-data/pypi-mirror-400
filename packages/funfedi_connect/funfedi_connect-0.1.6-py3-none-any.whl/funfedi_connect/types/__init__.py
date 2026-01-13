from enum import StrEnum, auto
import logging
import aiohttp

from collections.abc import Awaitable, Callable
from abc import abstractmethod

from bovine.clients import lookup_uri_with_webfinger

from .feature import ImplementedFeature
from .parsing import ParsingTestApplicationConfiguration

logger = logging.getLogger(__name__)

ApplicationPoster = Callable[[aiohttp.ClientSession, str], Awaitable[None]]
"""Describes how to post a message"""


class ApplicationConfiguration:
    """Configuration of an application to run tests with"""

    domain: str
    username: str
    application_name: str
    features: list[ImplementedFeature]

    @property
    def acct_uri(self):
        return f"acct:{self.username}@{self.domain}"

    async def _determine_actor_uri(self, session: aiohttp.ClientSession):
        actor_uri, _ = await lookup_uri_with_webfinger(
            session, self.acct_uri, f"http://{self.domain}"
        )
        return actor_uri

    @abstractmethod
    async def build_object_parsing(
        self, session: aiohttp.ClientSession
    ) -> ParsingTestApplicationConfiguration:
        """Builds the object parsing configuration"""

    @abstractmethod
    async def build_event_parsing(
        self, session: aiohttp.ClientSession
    ) -> ParsingTestApplicationConfiguration:
        """Builds the event parsing configuration"""

    @abstractmethod
    async def build_poster(self, session: aiohttp.ClientSession) -> ApplicationPoster:
        """Returns a function that allows posting a message"""


class Attachments(StrEnum):
    """Attachments added through allure.attach"""

    meta_data = auto()
    actor_object = auto()
    created_object = auto()
    send_activity = auto()
    timeline_item = auto()
    event_item = auto()
    webfinger_response = auto()
