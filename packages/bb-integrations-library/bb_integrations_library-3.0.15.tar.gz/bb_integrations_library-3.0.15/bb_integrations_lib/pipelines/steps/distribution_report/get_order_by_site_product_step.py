from datetime import datetime

from loguru import logger
from pandas.core.interchange.dataframe_protocol import DataFrame

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.pipelines import Step


class GetOrderBySiteProductStep(Step):
    def __init__(self, sd_client: GravitateSDAPI, include_model_mode: str = "latest_only", state: str = "accepted",
                 start_date: datetime | None = None, end_date: datetime | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.include_model_mode = include_model_mode
        self.state = state
        self.start_date = start_date
        self.end_date = end_date

    def describe(self) -> str:
        return f"Get orders by site product"

    async def execute(self, latest_model: dict | list) -> str | DataFrame:
        if "orders_by_site_product" not in self.pipeline_context.extra_data:
            self.pipeline_context.extra_data["orders_by_site_product"] = []
        if isinstance(latest_model, dict):
            return await self.get_orders_in_model_id(str(latest_model["_id"]))
        elif isinstance(latest_model, list):
            return [await self.get_orders_in_model_id(str(model["_id"])) for model in latest_model]
        else:
            raise ValueError("latest_model must be a dict or a list of dicts")

    async def get_orders_in_model_id(self, model_id: str, market: str | None = None) -> str | DataFrame:
        filter = self.build_filter()
        json_data = {
            'filter': {"lp_relationship.solver_id": str(model_id)
                       },
            'market': market if market else "",
        }

        response = await self.sd_client.call_ep(url="order/export_by_site_product",
                                                json=json_data
                                                )
        orders = response.content.decode("utf-8")
        if not hasattr(self, "custom_parser"):
            response = orders
        else:
            logger.info(f"Using custom parser for {self.__class__.__name__}")
            parser = self.custom_parser()
            response = await parser.parse(orders)
        self.pipeline_context.extra_data["orders_by_site_product"].append(response)
        return response

    def build_filter(self):
        filter = {
            "state": self.state,
        }
        if self.start_date:
            filter["From"] = self.start_date.isoformat()
        if self.end_date:
            filter["To"] = self.end_date.isoformat()
        return filter
