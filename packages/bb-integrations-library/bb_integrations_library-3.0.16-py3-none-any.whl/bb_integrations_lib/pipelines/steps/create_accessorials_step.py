import json
from time import sleep
from typing import Dict, List

from loguru import logger

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import CustomJSONEncoder


class BBDUploadAccessorialsStep(Step):
    def __init__(
            self,
            sd_client: GravitateSDAPI,
            buffer: float = 0.5,
            chuk_size: int = 1000,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.buffer = buffer
        self.chuk_size = chuk_size

    def describe(self) -> str:
        return "Upload Accessorials to BBD"

    async def execute(self, accessorials: List[Dict]) -> BBDUploadResult:
        logs = {"requests": [], "responses": [], "errors": []}
        try:
            total_accessorials = len(accessorials)
            succeeded = []
            failed_items = []

            for idx, accessorial in enumerate(accessorials):
                logs["requests"].append(accessorial)
                try:
                    resp = await self.sd_client.call_ep("freight/accessorial/automatic/rate/create", json=accessorial)
                    resp.raise_for_status()
                    _json = resp.json()
                    sleep(self.buffer)
                    succeeded.append(accessorial)
                    logger.info(f"Accessorials uploaded successfully: {idx + 1} of {total_accessorials}")
                    logs["responses"].append({"response": _json, "request": accessorial})
                except Exception as e:
                    logs["errors"].append({"record": accessorial, "error": f"Error uploading accessorials: {str(e)} {e.response.content}"})
                    failed_items.append(accessorial)
                    continue

            self.pipeline_context.included_files["accessorials data upload"] = json.dumps(logs, cls=CustomJSONEncoder)
            return BBDUploadResult(
                succeeded=len(succeeded),
                failed=len(failed_items),
                succeeded_items=succeeded
            )

        except Exception as e:
            logger.exception(f"Unable to upload | {e}")
            raise e
