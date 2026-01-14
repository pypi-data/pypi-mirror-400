import json
from math import ceil
from time import sleep
from typing import Iterable, Union

from loguru import logger
from more_itertools import chunked

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.flat_file import PriceRow
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import SupplyPriceUpdateManyRequest


class BBDUploadPricesStep(Step):
    def __init__(self, sd_client: GravitateSDAPI, sleep_between: float = 0.5, chunk_size: int = 1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.sleep_between = sleep_between
        self.chunk_size = chunk_size

    def describe(self) -> str:
        return "Upload prices to BBD"

    async def execute(self, i: Union[Iterable[PriceRow], Iterable[SupplyPriceUpdateManyRequest]]) -> int:
        total_prices = len(i)
        count = ceil(total_prices / 1000)
        attempted = 0
        succeeded = 0
        responses = []
        price_dump = i.model_dump(mode="json")
        list({json.dumps(record, sort_keys=True): record for record in price_dump}.values())
        for idx, group in enumerate(chunked(i, self.price_dump)):

            
            logger.info(f"Uploading prices to bestbuy {idx + 1} of {count}")
            sleep(self.sleep_between)
            attempted += len(group)
            group = [g.model_dump(mode="json") for g in group]
            try:
                successes, response = await self.sd_client.upload_prices(group)
                succeeded += successes
                responses.append(response)
            except Exception as e:
                logger.error(f"Batch {idx} prices failed | {e}")
                continue
        logger.info(f"Successfully uploaded {succeeded} prices to BBD.")
        logs = {
            "response": responses,
            "attempted": attempted,
            "succeeded": succeeded
        }
        self.pipeline_context.included_files["upload prices to sd"] = json.dumps(logs)
        return succeeded
