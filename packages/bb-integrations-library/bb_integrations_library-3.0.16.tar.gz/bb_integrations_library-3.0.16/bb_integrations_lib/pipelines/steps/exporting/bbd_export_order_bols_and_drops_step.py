import asyncio
import json
import uuid
from datetime import datetime, UTC
from io import BytesIO
from typing import List, Dict

import bson
from bb_integrations_lib.pipelines.shared.allocation_matcher.matching_utils import match_allocations
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import PipelineContext
from bb_integrations_lib.shared.model import SDGetUnexportedOrdersResponse, GetOrderBolsAndDropsRequest, \
    SDSetOrderExportStatusRequest, ERPStatus, RawData
from bb_integrations_lib.protocols.pipelines import Step, ParserBase
from bson import ObjectId
from loguru import logger
from pymongo.asynchronous.database import AsyncDatabase

from pymongo.synchronous.collection import Collection
from bson.raw_bson import RawBSONDocument
import pandas as pd


class BBDExportBolsAndDrops(Step):
    _allocation_semaphore: asyncio.Semaphore | None = None

    def __init__(self,
                 sd_client: GravitateSDAPI | None = None,
                 mongo_client: AsyncDatabase | None = None,
                 step_key: str | None = uuid.uuid4().hex,
                 file_base_name: str = "Gravitate_Order_Export",
                 use_raw_bson: bool = True,
                 test_order_ids: List[str] | None = None,
                 parser: ParserBase | None = None,
                 parser_kwargs: dict | None = None,
                 include_allocation_matching: bool = False,
                 allocation_max_concurrent: int = 10,
                 *args,
                 **kwargs):
        super().__init__(*args,
                         **kwargs)
        if self.pipeline_context is None:
            self.pipeline_context = PipelineContext()
        self.sd_client = sd_client
        self.mongo_client = mongo_client
        self.file_base_name = file_base_name
        self.use_raw_bson = use_raw_bson
        self.test_override_order_ids = test_order_ids
        self.include_allocation_matching = include_allocation_matching
        self.allocation_max_concurrent = allocation_max_concurrent
        self.step_key = step_key

        if sd_client and mongo_client:
            raise ValueError("Cannot use both SD API and DB client.")
        if not sd_client and not mongo_client:
            raise ValueError("Must provide either sd_client or mongo_client.")

        self.use_db = mongo_client is not None
        self.use_api = sd_client is not None

        if parser:
            self.custom_parser: type[ParserBase] = parser
            self.custom_parser_kwargs = parser_kwargs

    def describe(self):
        return "Get Bols and Drops from Supply and Dispatch"

    async def execute(self, orders: List[SDGetUnexportedOrdersResponse] | None = None) -> RawData:
        if self.test_override_order_ids is not None:
            order_bols_and_drops = await self.get_orders(self.test_override_order_ids)
        else:
            order_ids = [order.order_id for order in orders]
            order_bols_and_drops = await self.get_orders(order_ids)

        if self.include_allocation_matching and self.use_api:
            order_bols_and_drops = await self.add_allocation_matching_info(
                order_bols_and_drops
            )

        return self.parse(order_bols_and_drops)

    def parse(self, data: List[Dict]) -> RawData:
        if hasattr(self, "custom_parser"):
            parser = self.custom_parser(**self.custom_parser_kwargs)
            rows, processed, errors = parser.parse(data)
            self.collect_parser_results(errors, processed)
            return self.to_raw_data(rows)
        else:
            return self.to_raw_data(data)

    def to_raw_data(self, data: list[dict]) -> RawData:
        now = datetime.now(UTC)
        df = pd.DataFrame(data)
        csv_str = df.to_csv(index=False).encode("utf-8")
        file_name = f"{self.file_base_name}_{now.strftime('%Y%m%d%H%M%S')}.csv"
        return RawData(file_name=file_name, data=BytesIO(csv_str))

    def collection_with_options(self, collection: Collection):
        if self.use_raw_bson:
            return collection.with_options(
                codec_options=collection.codec_options.with_options(document_class=RawBSONDocument))
        else:
            return collection

    async def get_orders(self, order_ids: List[str]) -> List[Dict]:
        if self.use_api:
            return await self.get_orders_from_api(order_ids)
        else:
            return self.get_orders_from_db(order_ids)

    async def get_orders_from_api(self, order_ids: List[str]) -> List[Dict]:
        req = GetOrderBolsAndDropsRequest(order_ids=order_ids)
        response = await self.sd_client.get_bols_and_drops(req)
        return response.json()

    def get_orders_from_db(self, order_ids: List[str]) -> List[Dict]:
        collection = self.collection_with_options(self.db["order_v2"])
        data = list(collection.find({"_id": {"$in": [ObjectId(oid) for oid in order_ids]}}))
        if self.use_raw_bson:
            return [bson.decode(doc.raw) for doc in data]
        return data

    def collect_parser_results(self, errors, processed):
        errored_orders = [
            SDSetOrderExportStatusRequest(
                order_id=str(order.get("_id") or order.get('order_id')),
                status=ERPStatus.errors,
                error=order.get("error_message"),
            )
            for order in errors
        ]
        processed_orders = [
            SDSetOrderExportStatusRequest(
                order_id=str(order.get("_id") or order.get('order_id')),
                status=ERPStatus.sent,
            )
            for order in processed
        ]
        self.pipeline_context.extra_data["errored_orders"] = errored_orders
        self.pipeline_context.extra_data["processed_orders"] = processed_orders
        errored_json = json.dumps([order.model_dump() for order in errored_orders], indent=2)
        processed_json = json.dumps([order.model_dump() for order in processed_orders], indent=2)
        self.pipeline_context.included_files[f"{self.step_key} - errored orders"] = errored_json
        self.pipeline_context.included_files[f"{self.step_key} - processed orders"] = processed_json
        return errored_orders, processed_orders

    @property
    def allocation_semaphore(self) -> asyncio.Semaphore:
        if self._allocation_semaphore is None:
            self._allocation_semaphore = asyncio.Semaphore(self.allocation_max_concurrent)
        return self._allocation_semaphore

    async def get_planned_order(
            self,
            order_number: str | int,
    ) -> tuple[str, dict | None, str | None]:
        """
        Get planned order details for an order.

        Returns:
            tuple of (order_number, planned_order_dict, error_message)
        """
        async with self.allocation_semaphore:
            try:
                resp = await self.sd_client.get_orders(order_number=str(order_number))
                data = resp.json()
                return str(order_number), data[0] if data else None, None
            except Exception as e:
                logger.warning(f"Failed to get planned order {order_number}: {e}")
                return str(order_number), None, str(e)

    async def get_planned_orders(
            self,
            order_numbers: list[str | int],
    ) -> dict[str, dict | None]:
        """
        Fetch planned orders for multiple order numbers concurrently.

        Returns:
            Dict mapping order_number (str) -> planned_order dict (or None if failed)
        """
        order_strs = [str(n) for n in order_numbers]
        results = await asyncio.gather(
            *[self.get_planned_order(n) for n in order_strs]
        )
        return {order_num: planned for order_num, planned, _ in results}

    async def add_allocation_matching_info(
            self,
            order_bols_and_drops: List[Dict],
    ) -> List[Dict]:
        """
        For each order:
        1. Get planned order data
        2. Run allocation matching
        3. Add 'matched_allocations' to the order

        Args:
            order_bols_and_drops: List of bols_and_drops responses (one per order)

        Returns:
            The same list + 'matched_allocations' field
        """
        order_numbers = [
            bd.get("order_number")
            for bd in order_bols_and_drops
            if bd.get("order_number")
        ]

        planned_orders = await self.get_planned_orders(order_numbers)

        for order_data in order_bols_and_drops:
            order_num = str(order_data.get("order_number", ""))
            planned_order = planned_orders.get(order_num)

            try:
                allocated_bols = order_data.get("allocated_bols", [])
                executed_bols = order_data.get("bols", [])
                executed_drops = order_data.get("drops", [])
                planned_loads = planned_order.get("loads", []) if planned_order else []
                planned_drops = planned_order.get("drops", []) if planned_order else []

                if not allocated_bols and not planned_drops:
                    order_data["matched_allocations"] = []
                    continue

                matched = match_allocations(
                    order_number=order_num,
                    allocated_bols=allocated_bols,
                    executed_bols=executed_bols,
                    executed_drops=executed_drops,
                    planned_loads=planned_loads,
                    planned_drops=planned_drops,
                )

                order_data["matched_allocations"] = [
                    ma.model_dump() for ma in matched
                ]

            except Exception as e:
                logger.warning(f"Allocation matching failed for order {order_num}: {e}")
                order_data["matched_allocations"] = []

        return order_bols_and_drops


if __name__ == "__main__":
    sd_client = GravitateSDAPI(base_url="https://bazco.bb.gravitate.energy/", client_id="", client_secret="")

    import asyncio


    async def run_test(
            order_ids: list[str],
            sd_client: GravitateSDAPI | None = None,
    ):
        ppl = BBDExportBolsAndDrops(sd_client=sd_client, test_order_ids=order_ids, include_allocation_matching=True)
        orders = await ppl.execute()
        return orders


    asyncio.run(run_test(
        ["6953f0219ec64a986500addf", "695c69ef30e1e58f036ead7f", "695c6c0a3f666618ce00b065", "695e9f3f626ffa6c6ebcb307",
         "695fc66d626ffa6c6ebcb8b7", "695ffdfb626ffa6c6ebcb910"], sd_client))
