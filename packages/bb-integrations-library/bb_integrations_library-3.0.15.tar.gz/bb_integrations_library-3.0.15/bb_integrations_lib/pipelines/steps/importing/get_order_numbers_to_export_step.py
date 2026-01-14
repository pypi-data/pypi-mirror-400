import enum
from datetime import datetime, UTC, timedelta
from typing import Any, List

import pandas_gbq
from google.oauth2 import service_account
from loguru import logger
import pandas as pd
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from bb_integrations_lib.models.pipeline_structs import StopPipeline, StopBranch
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import init_db

class OrderType(enum.Enum):
    ANY = enum.auto()
    NOT_BACKHAUL = enum.auto()
    BACKHAUL_ONLY = enum.auto()

    def to_mongo_query(self):
        match self:
            case OrderType.ANY:
                return {}
            case OrderType.NOT_BACKHAUL:
                return {"type": {"$ne": "backhaul"}}
            case OrderType.BACKHAUL_ONLY:
                return {"type": "backhaul"}

    def __str__(self) -> str:
        return {
            OrderType.ANY: "any",
            OrderType.NOT_BACKHAUL: "not backhaul",
            OrderType.BACKHAUL_ONLY: "backhaul only",
        }[self]

class GetOrderNumbersToExportStep(Step):
    def __init__(self, mongo_database: Database, order_type_filter: OrderType, exported_order_table_name: str,
                 project_id: str, gcp_credentials_file: str, testing_date_min: datetime | None = None,
                 testing_date_max: datetime | None = None, lookback_days: int = 60, use_old_change_query: bool = False,
                 check_for_updated_orders: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mongo_database = mongo_database
        self.order_type_filter = order_type_filter
        self.exported_order_table_name = exported_order_table_name
        self.project_id = project_id
        self.gcp_credentials_file = gcp_credentials_file
        self.testing_date_min = testing_date_min
        self.testing_date_max = testing_date_max
        self.lookback_days = lookback_days
        self.use_old_change_query = use_old_change_query
        self.check_for_updated_orders = check_for_updated_orders
        if not self.gcp_credentials_file.endswith(".json"):
            self.gcp_credentials_file += ".json"

    def describe(self) -> str:
        return "Determine which order numbers to export."

    async def execute(self, i: Any) -> List[int]:
        collection = self.mongo_database["order_v2"]
        if not self.testing_date_min and not self.testing_date_max:
            lookback_date = datetime.now(UTC) - timedelta(days=self.lookback_days)
            date_query = {'$or': [
                {'updated_on': {'$gte': lookback_date}},
                {'movement_updated': {'$gte': lookback_date}}
            ]}
            logger.debug(f"Looking for orders in the previous {self.lookback_days} days.")
        elif self.testing_date_min and self.testing_date_max:
            date_query = {'$or': [
                {'updated_on': {'$gte': self.testing_date_min, '$lte': self.testing_date_max}},
                {'movement_updated': {'$gte': self.testing_date_min, '$lte': self.testing_date_max}}
            ]}
            logger.debug(f"Looking for orders between {self.testing_date_min} and {self.testing_date_max}")
        else:
            raise RuntimeError("testing_date_max and testing_date_min must provided together, or both not provided.")

        if self.use_old_change_query:
            change_query = {"change_date": "$updated_on"}
        else:
            change_query = {"change_date": { "$max": ["$updated_on", "$movement_updated"] }}

        # Over time the number of orders will grow. To keep step performance constant we're only going to look at
        # orders updated within the last 60 days
        assert isinstance(self.order_type_filter, OrderType)
        logger.debug(f"Searching for orders of type: {str(self.order_type_filter)}")
        orders = list(collection.find({**date_query,
                                       **self.order_type_filter.to_mongo_query(),
                                       "state": "complete"},
                                      {
                                          "_id": 0,
                                          "number": 1,
                                          **change_query,
                                      }))
        logger.debug(f"There are {len(orders)} orders updated in the last {self.lookback_days} days.")
        if len(orders) == 0:
            raise StopBranch()
        # We need to look up the list of exported orders from GBQ
        credentials = service_account.Credentials.from_service_account_file(self.gcp_credentials_file)
        sql = (f"select order_number as number, max(date) as exported_date"
               f" from `{self.exported_order_table_name}`"
               f" group by order_number;")
        gbq_df = pandas_gbq.read_gbq(sql, project_id=self.project_id, credentials=credentials, progress_bar_type=None)
        logger.debug(f"Received {gbq_df.shape[0]} GBQ records.")

        # Create a dataframe from the list of orders and do a left join on the orders exported from GBQ
        orders_df = pd.DataFrame.from_records(orders)
        joined = pd.merge(orders_df, gbq_df, on="number", how="left")

        never_exported = joined[joined["exported_date"].isna()]
        logger.debug(f"There are {never_exported.shape[0]} new orders to export.")

        if self.check_for_updated_orders:
            updated_after_export = joined[joined["exported_date"] < joined["change_date"]]
            logger.debug(f"There are {updated_after_export.shape[0]} orders that have been updated and need to be exported again.")
            to_export = set(never_exported["number"]).union(set(updated_after_export["number"]))
        else:
            to_export = set(never_exported["number"])

        output = list(to_export)
        logger.debug(output)
        if len(output) == 0:
            # There are no orders to export. Cancel the pipeline this step is part of.
            raise StopBranch()
        return output


if __name__ == "__main__":
    import asyncio
    async def main():
        s = GetOrderNumbersToExportStep(
            mongo_database=MongoClient("mongodb conn str")["db_name"],
            order_type_filter=OrderType.ANY,
            exported_order_table_name="gravitate-harms-prod.harms_order_exports.exported_backhaul_orders",
            project_id="gravitate-harms-prod",
            gcp_credentials_file="google.credentials.json"
        )
        await s.execute(None)
    asyncio.run(main())
