import httpx
from bb_integrations_lib.secrets import AnyCredential


class BaseAPI(httpx.AsyncClient):
    """
    I'm choosing to keep our BaseAPI client to add global \
    utility methods with ease in the future. \
    Wrap other API clients with this.
    """
    def __init__(self, raise_errors: bool = True):
        super().__init__()
        self.raise_errors = raise_errors

    @classmethod
    def from_credential(cls, credential: AnyCredential) -> "BaseAPI":
        raise NotImplementedError()

    async def close(self):
        await self.aclose()
