import json
from math import ceil
from time import sleep
from typing import List

from loguru import logger
from more_itertools import chunked

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult
from bb_integrations_lib.models.rita.issue import IssueBase, IssueCategory
from bb_integrations_lib.protocols.flat_file import TankReading
from bb_integrations_lib.protocols.pipelines import Step


class BBDUploadTankReadingStep(Step):
    """
    Takes a list of TankReading and uploads them to S&D, breaking them into chunks as required.

    :param sd_client: The GravitateSDAPI client to use for uploading.
    :param sleep_between: The number of seconds to sleep between each chunk.
    :param chunk_size: The maximum number of readings to upload in each chunk.
    """

    def __init__(self, sd_client: GravitateSDAPI, sleep_between: float = 0.5, chunk_size: int = 1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.sleep_between = sleep_between
        self.chunk_size = chunk_size

    def describe(self) -> str:
        return "Upload TankReadings to BBD"

    async def execute(self, i: List[TankReading]) -> BBDUploadResult:
        try:
            total_readings = len(i)
            count = ceil(total_readings / self.chunk_size)
            attempted = 0
            succeeded = 0
            included_set = set()
            failed = []
            for idx, group in enumerate(chunked(i, self.chunk_size)):
                logger.info(f"Uploading readings to bestbuy {idx + 1} of {count}")
                attempted += len(group)
                group = [g.model_dump(mode="json") for g in group]
                list({json.dumps(record, sort_keys=True): record for record in group}.values())
                try:
                    response = await self.sd_client.upload_readings(group, raise_error=False)
                    response = response.json()
                    succeeded += len(response["ids"])
                    included_set = included_set.union(set(response["ids"]))
                    if len(response["unable to upload"]) > 0:
                        logger.error(f"Errors occurred while uploading data: {response}")
                        failed = failed + response["unable to upload"]
                    sleep(self.sleep_between)
                except Exception as e:
                    logger.error(f"Batch {idx} readings failed | {e}")
                    failed = failed + [g["store"] for g in group]
                    continue
            logger.info(f"Successfully uploaded {succeeded} of {attempted} readings.")
            included_set = {x.split(":")[0] for x in included_set}

            if len(failed) > 0:
                logger.info(f"Failed to upload {len(failed)} of {attempted} readings")
                fc = self.pipeline_context.file_config
                key = f"{fc.config_id}_failed_to_upload"
                self.pipeline_context.issues.append(IssueBase(
                        key=key,
                        config_id=fc.config_id,
                        name="Failed to upload TankReadings",
                        category=IssueCategory.TANK_READING,
                        problem_short=f"{len(failed)} readings did not upload",
                        problem_long=json.dumps(failed)
                    ))

            return BBDUploadResult(succeeded=succeeded, failed=attempted - succeeded,
                                   succeeded_items=list(included_set))
        except Exception as e:
            logger.exception(f"Unable to upload | {e}")
            raise e
