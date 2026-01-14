import json
from math import ceil
from time import sleep
from typing import Dict, List

from loguru import logger
from more_itertools import chunked

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult
from bb_integrations_lib.models.rita.issue import IssueBase, IssueCategory
from bb_integrations_lib.protocols.flat_file import TankSales
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import CustomJSONEncoder


class BBDUploadTankSalesStep(Step):
    """
    Takes a list of TankSales and uploads them to Best Buy
    """

    def __init__(self, sd_client: GravitateSDAPI, sleep_between: float = 0.5, chunk_size: int = 1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.sleep_between = sleep_between
        self.chunk_size = chunk_size

    def describe(self) -> str:
        return "Upload Tanksales to BBD"

    async def execute(self, i: List[TankSales]) -> BBDUploadResult:
        logs = {"requests": [], "responses": [], "errors": []}
        try:
            total_sales = len(i)
            count = ceil(total_sales / self.chunk_size)
            attempted = 0
            succeeded = 0
            failed_items = []
            store_ids = []

            for idx, group in enumerate(chunked(i, self.chunk_size)):
                logger.info(f"Uploading sales to bestbuy {idx + 1} of {count} to: {self.sd_client.base_url}  ")
                attempted += len(group)
                serialized_group = [g.model_dump(mode="json") for g in group]
                batch_store_ids = [g.get("store_number", "unknown") for g in serialized_group]
                logs["requests"].append({
                    "row_id": idx,
                    "request": serialized_group,
                    "store_ids": batch_store_ids
                })

                try:
                    response: Dict = await self.sd_client.upload_tank_sales(serialized_group)
                    response_data = response
                    logs["responses"].append({
                        "row_id": idx,
                        "response": response_data,
                    })
                    created = response_data.get("created", 0)
                    updated = response_data.get("updated", 0)
                    failed = response_data.get("failed", [])
                    current_succeeded = created + updated
                    succeeded += current_succeeded
                    if current_succeeded > 0:
                        if current_succeeded == len(serialized_group) and not failed:
                            store_ids.extend(batch_store_ids)
                        else:
                            failed_store_numbers = [f["record"]["store_number"] for f in failed if
                                                    "record" in f and "store_number" in f["record"]]
                            failed_set = set(failed_store_numbers)
                            successful_ids = [
                                store_id for store_id in batch_store_ids
                                if store_id not in failed_set
                            ]
                            store_ids.extend(successful_ids)
                    if failed:
                        failed_items.extend(failed)
                        logs["errors"].append({
                            "row_id": idx,
                            "failed_items": failed,
                            "response": response_data
                        })
                        logger.error(f"Errors occurred while uploading data: {failed}")
                    logger.info(f"Batch {idx + 1}: Created {created}, Updated {updated}, Failed {len(failed)}")
                    sleep(self.sleep_between)
                except Exception as e:
                    error_msg = f"Batch {idx} sales failed | {e}"
                    logger.error(error_msg)
                    failed_items.extend(batch_store_ids)
                    logs["errors"].append({
                        "row_id": idx,
                        "exception": str(e),
                        "store_ids": batch_store_ids
                    })
                    continue

            logger.info(f"Successfully uploaded {succeeded} of {attempted} sales.")
            logger.info(f"Failed to upload {len(failed_items)} of {attempted} sales")
            if failed_items and hasattr(self.pipeline_context,
                                        'issue_report_config') and self.pipeline_context.issue_report_config:
                irc = self.pipeline_context.issue_report_config
                fc = self.pipeline_context.file_config
                key = f"{irc.key_base}_{fc.config_id}_failed_to_upload"
                self.pipeline_context.issues.append(IssueBase(
                    key=key,
                    config_id=fc.config_id,
                    name="Failed to upload Tanksales",
                    category=IssueCategory.TANK_READING,
                    problem_short=f"{len(failed_items)} sales did not upload",
                    problem_long=json.dumps(failed_items)
                ))

            self.pipeline_context.included_files["sales data upload"] = json.dumps(logs, cls=CustomJSONEncoder)
            return BBDUploadResult(
                succeeded=succeeded,
                failed=len(failed_items),
                succeeded_items=store_ids
            )

        except Exception as e:
            logger.exception(f"Unable to upload | {e}")
            raise e
