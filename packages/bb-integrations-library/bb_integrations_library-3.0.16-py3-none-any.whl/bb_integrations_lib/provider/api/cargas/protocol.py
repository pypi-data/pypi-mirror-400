from bb_integrations_lib.provider.api.cargas.model import CreateWholesaleTicketRequest, CreateWholesaleLineRequest, \
    CreateWholesaleFeeLineRequest


class CargasClient():
    def __init__(self,
                 api_key: str,
                 base_url: str = " https://cargase.aeroenergy.com/cargasenergy/API"):
        self.base_url = base_url
        self.api_key = api_key

    @property
    def custom_headers(self) -> dict:
        return {
            'APIKey': self.api_key,
            'Content-Type': 'application/json'
        }

    async def create_wholesale_ticket(self, data: CreateWholesaleTicketRequest): ...

    async def create_wholesale_line(self, data: CreateWholesaleLineRequest): ...

    async def create_wholesale_fee_line(self, data: CreateWholesaleFeeLineRequest): ...
