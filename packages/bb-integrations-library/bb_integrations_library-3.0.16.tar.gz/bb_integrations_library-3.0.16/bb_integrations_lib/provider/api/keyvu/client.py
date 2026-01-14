import httpx
from httpx import Request, Response

from bb_integrations_lib.provider.api.keyvu.model import KeyVuDeliveryPlan, default_serialization_options


class KeyVuAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request: Request):
        request.headers["Keyvu-Api-Key"] = self.token
        yield request


class KeyVuClient:
    def __init__(self, api_key: str):
        self.base_url = ""
        self.api_key = api_key
        self.client = httpx.AsyncClient(auth=KeyVuAuth(self.api_key))

    def build_url(self, tail: str) -> str:
        return f"{self.base_url}/{tail}"

    async def upload_deliveryplan(self, data: KeyVuDeliveryPlan, override_filename: str | None = None) -> Response:
        return await self.client.post(
            url=self.build_url("upload/deliveryplan"),
            content=data.to_xml(**default_serialization_options),
            headers={"filename": override_filename} if override_filename else {}
        )
