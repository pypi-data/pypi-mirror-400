from dataclasses import dataclass

import aiohttp


@dataclass
class LemmyObjectGetter:
    domain: str

    async def fetch_object(self, session: aiohttp.ClientSession, object_id: str):
        try:
            resp = await session.get(f"http://{self.domain}/api/v3/post/list")
            data = await resp.json()
            for post in data.get("posts"):
                data = post.get("post")
                if data.get("ap_id") == object_id:
                    return data
        except Exception as e:
            print(e)
        return None
