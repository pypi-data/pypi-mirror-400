import json
from time import sleep
from typing import Dict, List, cast

from loguru import logger

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import CustomJSONEncoder
from bb_integrations_lib.util.config.manager import GlobalConfigManager
from bb_integrations_lib.util.config.model import GlobalConfig


class BBDUploadAccessorialsStep(Step[List, BBDUploadResult, None]):

    def __init__(self, step_configuration: Dict[str, str]):
        super().__init__(step_configuration)
        self.config_manager = GlobalConfigManager()
        self.env_mode = step_configuration.get('mode', "production")
        self.buffer = step_configuration.get('buffer', 0.5)
        self.chuk_size = step_configuration.get('chuk_size', 1000)
        if 'env' in step_configuration:
            self.bbd_client = GravitateSDAPI.from_config(step_configuration["env"],
                                                         step_configuration["bbd_username"],
                                                         step_configuration["bbd_password"])
            self.bbd_client.username = step_configuration["bbd_username"]
            self.bbd_client.password = step_configuration["bbd_password"]
        elif 'tenant_name' in step_configuration:
            self.secret_data: GlobalConfig = self.config_manager.get_environment(step_configuration["tenant_name"])
            if self.env_mode == 'production':
                self.bbd_client = cast(GravitateSDAPI,
                                       self.config_manager.environment_from_name(step_configuration["tenant_name"],
                                                                                 "production",
                                                                                 sd_basic_auth=True).sd.api_client)
            else:
                logger.debug("Initializing API in dev mode")
                self.bbd_client = cast(GravitateSDAPI,
                                       self.config_manager.environment_from_name(step_configuration["tenant_name"],
                                                                                 "test",
                                                                                 sd_basic_auth=True).sd.api_client)

        else:
            raise Exception("env or tenant is required")

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
                    resp = await self.bbd_client.call_ep("freight/accessorial/automatic/rate/create", json=accessorial)
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
