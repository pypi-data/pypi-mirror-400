from async_lru import alru_cache
from typing import Optional, Dict, Self
from httpx import Response
from tenacity import retry, stop_after_attempt, wait_fixed

from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.secrets import PECredential


class GravitatePEAPI(BaseAPI):
    def __init__(
            self,
            base_url: str | None = None,
            username: str | None = None,
            password: str | None = None,
            raise_errors: bool = True,
    ):
        super().__init__(raise_errors)
        self.base_url = self.valid_url(base_url)
        self.username = username
        self.password = password


    @staticmethod
    def valid_url(url: str) -> str:
        if not url:
            return ""
        if not url.endswith("/"):
            url += "/"
        if "api" not in url and ":80" not in url and "local"not in url: #MOFO
            url += "api/"
        if not url.startswith("http"):
            raise ValueError(f"Invalid URL: {url} must begin with http or https")
        return url

    @alru_cache(maxsize=2)
    async def _get_token(self):
        try:
            if self.username and self.password:
                resp = await self.post(
                    url=f"{self.base_url}token/authorize",
                    data={
                        "username": self.username,
                        "password": self.password,
                        "scope": "bbd",
                    },
                    timeout=120
                )
            else:
                raise RuntimeError(
                    "Provide (username, password) to the GravitatePEAPI")
        except Exception as e:
            raise ValueError(f"Error Getting Token for {self.base_url}")
        try:
            return resp.json()["access_token"]
        except:
            raise ValueError(
                f"Could Not Get Token for {self.base_url} -> {resp.status_code}"
            )

    @classmethod
    def from_credential(cls, credential: PECredential) -> Self:
        return cls(
            base_url=credential.host,
            username=credential.username,
            password=credential.password,
        )

    async def token_post(self, **kwargs) -> Response:
        headers = kwargs.get("headers", {})
        headers = {**headers, "authorization": f"Bearer {await self._get_token()}"}
        url = kwargs.get("url", "")
        url = f"{self.base_url}{url}"
        kwargs = kwargs | {"url": url, "headers": headers}
        return await self.post(**kwargs)

    async def token_get(self, **kwargs) -> Response:
        headers = kwargs.get("headers", {})
        headers = {**headers, "authorization": f"Bearer {await self._get_token()}"}
        url = kwargs.get("url", "")
        url = f"{self.base_url}{url}"
        kwargs = kwargs | {"url": url, "headers": headers}
        return await self.get(**kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def call_ep(self, url: str, payload: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        return await self.token_post(url, payload, json)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def get_contracts(self, payload: Dict):
        url = "extract/contractManagement/contract/ByQuery"
        return (await self.token_post(url=url, json=payload)).json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def get_prices(self, payload: Dict) -> Dict:
        url = "extract/price/ByQuery"
        return (await self.token_post(url=url, json=payload)).json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def bulk_sync_price_structure(self, payload: Dict) -> Dict:
        url = "integration/pricing/BulkSyncPriceStructure"
        return (await self.token_post(url=url, json=payload)).json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def merge_prices(self, payload: Dict) -> Dict:
        url = "integration/pricing/Merge"
        return (await self.token_post(url=url, json=payload)).json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def integration_start(self, payload: Dict):
        url = "Integration/IntegrationStatus/IntegrationStart"
        return (await self.token_post(url=url, payload=payload)).json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def integration_stop(self, payload: Dict):
        url = "Integration/IntegrationStatus/IntegrationStop"
        return (await self.token_post(url=url, payload=payload)).json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def integration_error(self, payload: Dict):
        url = "Integration/IntegrationStatus/IntegrationError"
        return (await self.token_post(url=url, payload=payload)).json()
