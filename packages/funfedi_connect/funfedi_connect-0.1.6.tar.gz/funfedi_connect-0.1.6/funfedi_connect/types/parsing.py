import asyncio


from collections.abc import Callable, Awaitable
from dataclasses import dataclass

import aiohttp


ApplicationObjectGetter = Callable[[aiohttp.ClientSession, str], Awaitable[dict | None]]


@dataclass
class ParsingTestApplicationConfiguration:
    """Configuration for testing activity parsing by retrieving
    the parsed object by its id"""

    actor_id: str
    application_name: str
    base_object_getter: ApplicationObjectGetter

    poll_number: int = 5
    wait_time: float = 1

    async def object_getter(
        self, session: aiohttp.ClientSession, object_id: str
    ) -> dict | None:
        """Returns the parsing result or not if the result could not be retrieved, e.g.
        due to a parsing failure. Polling is used up to poll_number with wait_time seconds
        in between."""
        for _ in range(self.poll_number):
            result = await self.base_object_getter(session, object_id)
            if result:
                return result

            await asyncio.sleep(self.wait_time)

        return None
