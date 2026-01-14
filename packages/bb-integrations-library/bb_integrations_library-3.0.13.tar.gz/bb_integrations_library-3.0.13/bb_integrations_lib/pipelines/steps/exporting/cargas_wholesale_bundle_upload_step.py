from typing import Any

from bb_integrations_lib.protocols.pipelines import Step, Input, StepConfig
from loguru import logger

from bb_integrations_lib.provider.api.cargas.client import CargasClient
from bb_integrations_lib.provider.api.cargas.model import CreateWholesaleTicketRequest, \
    CreateWholesaleTicketRequestBundle


class CargasWholesaleBundleUploadStep(Step):
    def __init__(self, cargas_client: CargasClient, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cargas_client = cargas_client

    def describe(self):
        return "Upload a Cargas Wholesale ticket request bundle"

    async def execute(self, i: CreateWholesaleTicketRequestBundle) -> None:
        cwt_resp = await self.cargas_client.create_wholesale_ticket(i.ticket_request)
        doc_id = cwt_resp["ResponseValues"]["DocumentID"]

        # Now try to upload each line
        for index, line in enumerate(i.line_requests):
            try:
                line.DocumentID = int(doc_id)
                await self.cargas_client.create_wholesale_line(line)
            except Exception as e:
                logger.error(f"Failed to upload line {index} to Cargas: {e}")
        print(cwt_resp)

        # TODO: Upload fee line items
