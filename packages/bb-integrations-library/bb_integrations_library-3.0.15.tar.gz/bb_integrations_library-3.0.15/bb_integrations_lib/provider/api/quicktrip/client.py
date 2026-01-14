from typing import Self
import httpx

from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.secrets.credential_models import QTCredential


class QTApiClient(BaseAPI):
    def __init__(self,
                 base_url: str,
                 qt_id: str,
                 carrier_id: str,
                 authorization: str):
        super().__init__()
        self.base_url = base_url
        self.qt_id = qt_id
        self.carrier_id = carrier_id
        self.authorization = authorization

    @classmethod
    def from_credential(cls, credential: QTCredential) -> Self:
        return cls(**credential.model_dump(exclude={"type_tag"}))

    async def get_inventory(self) -> list[dict]:
        params = {
        "qtId": self.qt_id,
            "carrierId": self.carrier_id,
            "authorization": self.authorization
        }
        response = await self.get(
            f"{self.base_url}/api/ExternalEndpoint/GetLatestCarrierInventory",
            params=params
        )
        response.raise_for_status()
        return response.json()



if __name__ == "__main__":
    import asyncio

    async def main():
        client = QTApiClient(
            base_url="https://petrocorpapi.quiktrip.com",
            qt_id="EAGN",
            carrier_id="41",
            authorization="07572AD2B28DC42410D7CAD4ED126499FDE84F73A7D4A56CE2A1ADBE80117FDD10DC7923E9CFB06BF03FF9251CADD2F2163F7C341E954656FE046F3EC932CD7F"
        )
        inventory = await client.get_inventory()
        print(inventory)

    asyncio.run(main())