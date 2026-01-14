import json
import uuid
from typing import Any, List, Dict

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.shared.model import SDGetUnexportedOrdersRequest, SDGetUnexportedOrdersResponse
from bb_integrations_lib.protocols.pipelines import Step
from datetime import datetime, UTC


class BBDGetOrdersToExportStep(Step):
    def __init__(self,
                 sd_client: GravitateSDAPI,
                 step_key: str | None = uuid.uuid4().hex,
                 target_date: datetime | None = None,
                 test_order_numbers: List[str] | None = None,
                 *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.step_key = step_key
        self.sd_client = sd_client
        self.target_date = target_date
        self.test_override_order_numbers = test_order_numbers

    def describe(self):
        return "Get Orders to Export from Supply and Dispatch"

    async def execute(self, _: Any = None) -> List[SDGetUnexportedOrdersResponse]:
        last_sync_date = self.last_sync_date()
        orders, serialized = await self.get_orders_since_last_check_in(last_sync_date)
        if self.pipeline_context is not None:
            self.pipeline_context.extra_data[self.step_key] = {
                "date_used_in_api_call": last_sync_date,
                "orders": serialized,
                "total_orders": len(serialized),
            }
        return orders

    async def get_orders_since_last_check_in(self, last_check_in_date: datetime | None = None) -> tuple[List[
        SDGetUnexportedOrdersResponse], List[Dict]]:
        req = SDGetUnexportedOrdersRequest(
            as_of=last_check_in_date
        )
        orders = await self.sd_client.get_unexported_orders(
            req=req,
        )
        orders_json = orders.json()
        self.pipeline_context.included_files[self.step_key] = json.dumps(orders_json)
        if self.test_override_order_numbers is not None:
            orders_json = list(
                filter(lambda order: order["order_number"] in self.test_override_order_numbers, orders_json))
        return [SDGetUnexportedOrdersResponse.model_validate(order) for order in orders_json] or [], orders_json

    def last_sync_date(self) -> datetime:
        if self.target_date is not None:
            return self.target_date
        return datetime.now(UTC)


