from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import SDSupplierInvoiceCreateRequest


class UploadSupplierInvoiceStep(Step):
    def __init__(self, sd_client: GravitateSDAPI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client

    def describe(self) -> str:
        return "Upload a supplier invoice to S&D"

    async def execute(self, i: SDSupplierInvoiceCreateRequest) -> None:
        res = await self.sd_client.upload_supplier_invoice(i)
        res.raise_for_status()
