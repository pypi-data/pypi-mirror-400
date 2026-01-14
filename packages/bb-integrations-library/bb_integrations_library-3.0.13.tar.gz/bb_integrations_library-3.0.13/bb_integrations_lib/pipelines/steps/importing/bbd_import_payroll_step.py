from typing import Dict, Any

import loguru
from httpx import HTTPStatusError
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import FileReference, FileType
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI


class BBDImportPayrollStep(Step):
    def __init__(self, sd_client: GravitateSDAPI, output_file_path: str, bbd_date_argument: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.temp_file_path = output_file_path
        self.bbd_date_argument = bbd_date_argument

    def describe(self) -> str:
        return "Import Payroll from BBD"

    async def execute(self, _: Any) -> FileReference:
        try:
            payroll_resp = await self.sd_client.payroll_export(self.bbd_date_argument)
            # Download the file from the response
            if payroll_resp.status_code == 200:
                with open(self.temp_file_path, "wb") as f:
                    f.write(payroll_resp.content)

            return FileReference(self.temp_file_path, FileType.excel)
        except HTTPStatusError as e:
            loguru.logger.error(e.response.content)
