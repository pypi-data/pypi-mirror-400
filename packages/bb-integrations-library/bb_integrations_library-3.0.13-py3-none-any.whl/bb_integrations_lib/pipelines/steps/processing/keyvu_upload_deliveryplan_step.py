from datetime import datetime

import httpx
from loguru import logger

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.api.keyvu.model import KeyVuDeliveryPlan, default_serialization_options
from bb_integrations_lib.shared.model import RawData


class KeyVuUploadDeliveryPlanStep(Step):
    def __init__(self, endpoint_url: str, keyvu_api_key: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.endpoint_url = endpoint_url
        self.keyvu_api_key = keyvu_api_key

    def describe(self) -> str:
        return "Upload a KeyVu DeliveryPlan XML file to KeyVu"

    async def execute(self, i: KeyVuDeliveryPlan) -> RawData:
        logger.info("Serializing delivery plan")
        dp_file = i.to_xml(**default_serialization_options)

        logger.info(f"Uploading to {self.endpoint_url} ({len(dp_file)} bytes)")
        res = httpx.post(
            url=self.endpoint_url,
            content=dp_file,
            headers={"KeyVu-Api-Key": self.keyvu_api_key}
        )
        res.raise_for_status()
        logger.debug(f"Response code: {res.status_code}, response body: {res.content}")
        logger.info("Done")

        self.pipeline_context.included_files["Delivery Plan"] = dp_file

        return RawData(
            data=dp_file,
            file_name=f"plan_file{datetime.now().isoformat()}.xml"
        )
