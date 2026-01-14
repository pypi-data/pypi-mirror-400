from datetime import datetime, UTC
from enum import StrEnum
from time import monotonic
from typing import Any

import tenacity
from loguru import logger
from pymongo import UpdateOne
from tenacity import retry, wait_exponential

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import BolExportResults
from bb_integrations_lib.models.sd.orders import BackofficeERP, ERPStatus
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import init_db


class TooManyRequests(Exception):
    pass


class MarkOrdersExportedMethod(StrEnum):
    API = "api"
    BACKHAUL_API = "backhaul_api"
    DB = "db"


class MarkOrdersExportedInBBDStep(Step):
    """
    This step marks BolExportResult orders as exported in the order movements page.

    It supports 2 different marking methods:
      1. API method: Uses the S&D API, and runs an __always_succeed backoffice_erp function on every order. This is the
         default, and very slow.
      2. DB method: Directly modifies the S&D DB. Much faster, but subject to S&D schema changes.

    Note that ``BolExportResults.errors`` must be a dict in the form ``{"order_number": int, "error": str}``.

    **Limitations**:
    If using the API method, the __always_succeed function must be set in the target S&D tenant. Error messages cannot
    be set and will get discarded.
    """

    def __init__(self, order_number_key: str, export_method: MarkOrdersExportedMethod = MarkOrdersExportedMethod.API,
                 export_function_name: str | None = None, sd_client: GravitateSDAPI | None = None,
                 mongodb_conn_str: str | None = None, mongodb_db_name: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.export_method = export_method
        self.function_name = export_function_name
        self.order_number_key = order_number_key

        self.sd_client = sd_client
        self.mongodb_conn_str = mongodb_conn_str
        self.mongodb_db_name = mongodb_db_name

        match self.export_method:
            case MarkOrdersExportedMethod.API | MarkOrdersExportedMethod.BACKHAUL_API:
                logger.debug(f"Marking orders exported using {self.export_method} method")
            case MarkOrdersExportedMethod.DB:
                logger.debug("Marking orders exported using direct DB access method")

    def describe(self) -> str:
        return "Mark orders as exported in the order movements page"

    async def execute(self, i: BolExportResults) -> BolExportResults:
        unique_orders = list(set([int(order[self.order_number_key]) for order in i.orders]))
        match self.export_method:
            case MarkOrdersExportedMethod.API | MarkOrdersExportedMethod.BACKHAUL_API:
                await self._mark_all_exported_api(unique_orders)
            case MarkOrdersExportedMethod.DB:
                await self._mark_exported_db(unique_orders, i.errors)

        return i

    async def _mark_all_exported_api(self, unique_orders: list[int]):
        start_time = monotonic()
        n_orders = len(unique_orders)
        for index, number in enumerate(unique_orders):
            try:
                if self.export_method == MarkOrdersExportedMethod.API:
                    await self._mark_exported_api(number)
                else:
                    await self._mark_exported_backhaul_api(number)
                elapsed_time = monotonic() - start_time
                logger.info(
                    f"Marked order {number} done ({index + 1} of {n_orders}, {(index + 1) / n_orders:.0%}). "
                    f"Total elapsed: {int(elapsed_time)}s")
            except Exception as e:
                logger.warning(f"Unable to mark order as exported. {e}")

        logger.info(f"Finished processing {n_orders} orders in {int(monotonic() - start_time)}s")

    @retry(
        retry=tenacity.retry_if_exception_type(TooManyRequests),
        wait=wait_exponential(multiplier=1, min=5, max=30),
        stop=tenacity.stop_after_delay(60),
    )
    async def _mark_exported_api(self, number: int):
        """
        Use the S&D API to mark a single order as exported with an __always_succeed function.
        Less reliable and much slower than the DB method, and requires the __always_succeed function to be set in the
        target S&D tenant.
        """
        resp = await self.sd_client.export_single_order(number, self.function_name)
        logger.debug(f"Order {number} response status code: {resp.status_code}")
        if resp.status_code == 429:
            raise TooManyRequests()
        resp.raise_for_status()
        resp_json = resp.json()
        if len(resp_json) == 0:
            raise Exception(resp_json)

    @retry(
        retry=tenacity.retry_if_exception_type(TooManyRequests),
        wait=wait_exponential(multiplier=1, min=5, max=30),
        stop=tenacity.stop_after_delay(60),
    )
    async def _mark_exported_backhaul_api(self, number: int):
        """Use the S&D API to mark a single backhaul order as exported."""
        resp = await self.sd_client.mark_backhaul_exported(number)
        logger.debug(f"Order {number} response status code: {resp.status_code}")
        if resp.status_code == 429:
            raise TooManyRequests()
        resp.raise_for_status()
        resp_json = resp.json()
        if len(resp_json) == 0:
            raise Exception(resp_json)

    async def _mark_exported_db(self, unique_orders: list[int], errors: list[dict[str, Any]]):
        """
        Mark multiple orders as exported by manually twiddling the S&D DB. This avoids the reliability and
        performance issues of the API approach, and supports setting error text to be shown in the UI, but is at the
        mercy of the DB schema changing underneath us.

        :param unique_orders: List of order numbers to mark as exported / "sent"
        :param errors: List of errors to mark as failed, each in the format ``{"order_number": int, "error": str}``
        """
        sent_erp_obj = BackofficeERP(status=ERPStatus.sent, time_sent=datetime.now(UTC), errors=[]).model_dump()
        with init_db(self.mongodb_conn_str, self.mongodb_db_name) as db:
            # Mark successful exports
            if len(unique_orders) > 0:
                mark_sent_result = db["order_v2"].update_many(filter={"number": {"$in": unique_orders}},
                                           update={"$set": {"backoffice_erp": sent_erp_obj}})
                logger.info(f"Marked {mark_sent_result.modified_count} orders as exported")
            else:
                logger.info("No successfully exported orders to mark")

            # Mark failed exports with error messages
            update_list = [UpdateOne(
                    filter={"number": error["order_number"]},
                    update={"$set": {
                        "backoffice_erp": self._error_to_backoffice_erp_obj(error["error"]).model_dump()
                    }})
                for error in errors
            ]
            if len(update_list) > 0:
                mark_failed_result = db["order_v2"].bulk_write(update_list)
                logger.info(f"Marked {mark_failed_result.modified_count} orders as failed to export")
            else:
                logger.info("No export failures to mark")

    @staticmethod
    def _error_to_backoffice_erp_obj(error_message: str):
        return BackofficeERP(status=ERPStatus.errors, time_sent=datetime.now(UTC), errors=[error_message])


if __name__ == "__main__":
    import asyncio

    async def main():
        order_nums = [10000]
        orders = [{"OrderNumber":x} for x in order_nums]

        s = MarkOrdersExportedInBBDStep(
            order_number_key="OrderNumber",
            export_function_name="__always_succeed",
            export_method=MarkOrdersExportedMethod.API,
            sd_client=GravitateSDAPI(
                username="",
                password="",
                base_url="",
            ))
        await s.execute(BolExportResults(orders=orders, errors=[], file_name="oneoff", order_number_key="OrderNumber"))

    asyncio.run(main())
