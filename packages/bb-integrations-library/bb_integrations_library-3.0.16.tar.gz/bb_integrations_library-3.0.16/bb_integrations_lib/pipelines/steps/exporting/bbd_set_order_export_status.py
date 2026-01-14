import uuid
from typing import cast, List
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import NoPipelineData
from bb_integrations_lib.shared.model import ERPStatus, SDSetOrderExportStatusRequest, \
    SDGetUnexportedOrdersResponse
from bb_integrations_lib.protocols.pipelines import Step
from loguru import logger


class BBDSetExportOrderStatus(Step):
    def __init__(self,
                 sd_client: GravitateSDAPI,
                 step_key: str | None = uuid.uuid4().hex,
                 global_status_override: ERPStatus | None = None,
                 use_pipeline_context: bool = False,
                 *args,  **kwargs):
        super().__init__(*args,  **kwargs)
        self.step_key = step_key
        self.sd_client = sd_client
        self.global_status_override = global_status_override
        self.use_pipeline_context = use_pipeline_context

    def describe(self):
        return "Set Order Export Status in BBD"

    async def execute(self, orders: List[SDGetUnexportedOrdersResponse]) -> List[SDGetUnexportedOrdersResponse]:
        request = self.get_right_orders(orders)
        response = await self.sd_client.bulk_set_export_order_status(request)
        response.raise_for_status()
        return orders

    def get_right_orders(self, orders: List[SDGetUnexportedOrdersResponse] | None) -> List[SDSetOrderExportStatusRequest]:
        if self.use_pipeline_context and orders is None:
            pipeline_extra_data = self.pipeline_context.extra_data
            logger.warning("Usign Pipeline Context")
            logger.info("Orders should be stored -> processed: extra_data.processed_orders || errored: extra_data.errored_orders")
            if "processed_orders" not in pipeline_extra_data or "errored_orders" not in pipeline_extra_data:
                msg = "Unable to use context to set order status. Please use parameter instead"
                logger.error(msg)
                raise ValueError(msg)
            processed_orders = pipeline_extra_data.get("processed_orders")
            errored_orders = pipeline_extra_data.get("errored_orders")
            return processed_orders + errored_orders
        else:
            return self.format_set_order_status_request(orders)


    def format_set_order_status_request(self, orders: List[SDGetUnexportedOrdersResponse]) -> List[SDSetOrderExportStatusRequest]:
        if orders is None:
            raise NoPipelineData("Did not find any new orders to export")
        reqs = []
        for order in orders:
            if self.global_status_override:
                order.export_status = self.global_status_override
            req = SDSetOrderExportStatusRequest(
                order_id = order.order_id,
                status = order.export_status,
                error=order.error_message,
            )
            reqs.append(req)
        return reqs





