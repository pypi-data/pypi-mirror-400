from datetime import datetime, UTC
from typing import Self

from httpx import Response

from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.provider.api.platform_science.model import JobDefinition, LoadDefinition
from bb_integrations_lib.secrets.credential_models import PlatformScienceCredential


class PlatformScienceClient(BaseAPI):
    def __init__(self,
                 base_url: str,
                 client_id: str,
                 client_secret: str
                 ):
        super().__init__()
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None

    def __repr__(self):
        return "Platform Science API client"

    @classmethod
    def from_credential(cls, credential: PlatformScienceCredential) -> Self:
        return cls(
            base_url=credential.base_url,
            client_id=credential.client_id,
            client_secret=credential.client_secret,
        )

    async def _get_token(self):
        try:
            resp = await self.post(
                url=f"{self.base_url}oauth/token",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "api-version": "2.0"
                },
                json={
                    "grant_type": "client_credentials",
                    "scope": "admin workflow",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )
        except Exception:
            raise ValueError(f"Error getting token from {self.base_url}")

        try:
            self._token = resp.json()["access_token"]
            return self._token
        except Exception:
            raise ValueError(f"Token response invalid from {self.base_url} -> {resp.status_code}")

    async def _auth_request(self, method: str, **kwargs):
        if not self._token:
            await self._get_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"
        headers["api-version"] = "2.0"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers
        kwargs["url"] = f"{self.base_url}{kwargs.get('url', '')}"
        kwargs["timeout"] = kwargs.get("timeout", 90)

        response = await getattr(self, method)(**kwargs)

        if response.status_code == 401:
            await self._get_token()  # refresh token
            headers["authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers
            response = await getattr(self, method)(**kwargs)

        return response

    async def auth_post(self, **kwargs) -> Response:
        return await self._auth_request("post", **kwargs)

    async def auth_get(self, **kwargs) -> Response:
        return await self._auth_request("get", **kwargs)

    async def auth_patch(self, **kwargs) -> Response:
        return await self._auth_request("patch", **kwargs)

    async def auth_put(self, **kwargs) -> Response:
        return await self._auth_request("put", **kwargs)

    async def auth_delete(self, **kwargs) -> Response:
        return await self._auth_request("delete", **kwargs)

    async def paginated_get(self, url: str, params: dict | None = None) -> list[dict]:
        params = params or {}
        first_page = await self.auth_get(url=url, params=params)
        if first_page.status_code != 200:
            raise RuntimeError(f"Error getting assets from {self.base_url}")
        body = first_page.json()
        data = body["data"]
        total_pages = body["meta"]["pagination"]["total_pages"]
        while body["meta"]["pagination"]["current_page"] < total_pages:
            params["page"] = body["meta"]["pagination"]["current_page"] + 1
            next_page = await self.auth_get(url="admin/assets", params=params)
            body = next_page.json()
            data.extend(body["data"])
        return data

    async def get_assets(self) -> list[dict]:
        return await self.paginated_get(url="admin/assets")

    async def get_drivers(self) -> list[dict]:
        return await self.paginated_get(url="admin/drivers")

    async def create_assets(self, req: list[dict]) -> Response:
        return await self.auth_post(url="admin/assets", json=req)

    async def get_amqp_connection(self, channel_name: str):
        vhost = ""
        conn_str = f"amqps://{self.client_id}:{self.client_secret}@amqp.pltsci.com:5671/{vhost}"

    async def create_workflow_job(self, driver_id: str, job_definition: JobDefinition) -> Response:
        return await self.auth_post(url=f"drivers/{driver_id}/jobs", json={
            "job": job_definition.model_dump(mode="json", exclude_unset=True)
        })

    async def update_workflow_job(self, driver_id: str, job_id: str, job_definition: JobDefinition) -> Response:
        return await self.auth_put(url=f"drivers/{driver_id}/jobs/{job_id}", json={
            "job": job_definition.model_dump(mode="json", exclude_unset=True)
        })

    async def complete_workflow_job(self, job_id: str, completed_at: datetime | None = None) -> Response:
        return await self.auth_patch(url=f"jobs/{job_id}/status", json={
            "status": "tms_completed",
            "completed_at": (completed_at or datetime.now(tz=UTC)).astimezone(tz=UTC).isoformat()
        })

    async def delete_workflow_job(self, job_id: str) -> Response:
        return await self.auth_delete(url=f"jobs/{job_id}/status")

    async def create_load(self, driver_id: str, load_definition: LoadDefinition) -> Response:
        return await self.auth_post(
            url=f"admin/drivers/{driver_id}/loads",
            json=load_definition.model_dump(mode="json", exclude_none=False)
        )
