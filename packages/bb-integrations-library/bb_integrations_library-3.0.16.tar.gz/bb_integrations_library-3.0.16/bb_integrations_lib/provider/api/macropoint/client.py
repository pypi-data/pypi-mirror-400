import base64
from functools import lru_cache
import httpx
from httpx import Response
from bb_integrations_lib.provider.api.macropoint.model import LocationUpdateRequest


class MacropointClient(httpx.AsyncClient):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self._headers = {}

    @lru_cache(maxsize=1)
    async def _get_token(self):
        encoded = base64.standard_b64encode(f"{self.username}:{self.password}".encode()).decode()
        return f"Basic {encoded}"

    async def update_location(self, req: LocationUpdateRequest) -> Response:
        return await self.post(
            url="https://macropoint-lite.com/api/1.0/tms/data/location",
            headers={
                "Content-Type": "application/xml",
                "Authorization": await self._get_token(),
            },
            data=req.to_xml()
        )