import httpx

from bb_integrations_lib.provider.api.cargas.model import CreateWholesaleTicketRequest, CreateWholesaleFeeLineRequest, \
    CreateWholesaleLineRequest


class CargasClient(httpx.AsyncClient):
    def __init__(self,
                 api_key: str,
                 base_url: str = " https://cargase.aeroenergy.com/cargasenergy/API"):
        super().__init__(base_url=base_url)
        self.api_key = api_key

    @property
    def custom_headers(self) -> dict:
        return {
            'APIKey': self.api_key,
            'Content-Type': 'application/json'
        }

    async def create_wholesale_ticket(self, data: CreateWholesaleTicketRequest) -> dict:
        url = '/CreateWholesaleTicket'
        res = await self.post(
            url=url, headers=self.custom_headers, json=data.model_dump(exclude_none=True, mode="json")
        )
        res.raise_for_status()
        return res.json()

    async def create_wholesale_line(self, data: CreateWholesaleLineRequest) -> dict:
        url = '/CreateWholesaleLine'
        res = await self.post(
            url=url, headers=self.custom_headers, json=data.model_dump(exclude_none=True, mode="json")
        )
        res.raise_for_status()
        return res.json()

    async def create_wholesale_fee_line(self, data: CreateWholesaleFeeLineRequest) -> dict:
        url = '/CreateWholesaleFeeLine'
        res = await self.post(
            url=url, headers=self.custom_headers, json=data.model_dump(exclude_none=True, mode="json")
        )
        res.raise_for_status()
        return res.json()
