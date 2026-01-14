import json
from typing import Dict, List

from bb_integrations_lib.gravitate.pe_api import GravitatePEAPI
from bb_integrations_lib.util.utils import CustomJSONEncoder
from bb_integrations_lib.util.config.manager import GlobalConfigManager
from bb_integrations_lib.util.config.model import GlobalConfig
from loguru import logger
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult, UploadResult
from bb_integrations_lib.models.rita.issue import IssueBase, IssueCategory
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.protocols.flat_file import PePriceMergeIntegration


class PEPriceMerge(Step[List[PePriceMergeIntegration], BBDUploadResult, None]):
    def __init__(self, step_configuration: Dict[str, str]):
        super().__init__(step_configuration)
        self.config_manager = GlobalConfigManager()
        self.env_mode = step_configuration.get('mode', "production")
        self.tenant_name = step_configuration.get('tenant_name', None)
        if 'pe_client_base_url' in step_configuration:
            self.client_base_url = step_configuration['pe_client_base_url']
            self.username = step_configuration['pe_username']
            self.password = step_configuration['pe_password']
            self.client_name = step_configuration['client_name']
            self.pe_integration_client = GravitatePEAPI(
                base_url=self.client_base_url,
                username=self.username,
                password=self.password)

        else:
            if self.tenant_name is None:
                raise ValueError("'tenant_name' or pe client base url are required")
            self.secret_data: GlobalConfig = self.config_manager.get_environment(self.tenant_name)
            if self.env_mode == 'production':
                self.pe_integration_client = GravitatePEAPI(
                    base_url=self.secret_data.prod.pe.base_url,
                    username=self.secret_data.prod.pe.username,
                    password=self.secret_data.prod.pe.password,
                )
            else:
                logger.debug("Initializing API in dev mode")
                self.pe_integration_client = GravitatePEAPI(
                    base_url=self.secret_data.test.pe.base_url,
                    username=self.secret_data.test.pe.username,
                    password=self.secret_data.test.pe.password,
                )

    def describe(self) -> str:
        return "Merge Prices in Pricing Engine"

    async def execute(self, i: List[PePriceMergeIntegration]) -> BBDUploadResult:
        failed_rows: List = []
        success_rows: List = []
        responses: List = []
        try:
            for row in i:
                row_dump = row.model_dump(exclude_none=True)
                try:
                    response = await self.pe_integration_client.merge_prices(row_dump)
                    success_rows.append({**row_dump, "response": response})
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Failed to merge row: {e}")
                    failed_rows.append(row_dump)
                    continue
        except Exception as e:
            if irc := self.pipeline_context.issue_report_config:
                fc = self.pipeline_context.file_config
                key = f"{irc.key_base}_{fc.config_id}_failed_to_upload"
                self.pipeline_context.issues.append(IssueBase(
                    key=key,
                    config_id=fc.config_id,
                    name="Failed to merge price row",
                    category=IssueCategory.PRICE,
                    problem_short=f"{len(failed_rows)} rows failed to price merge",
                    problem_long=json.dumps(failed_rows)
                ))
        logs = {
            "request": [l.model_dump() for l in i],
            "response": responses
        }
        self.pipeline_context.included_files["price merge data"] = json.dumps(logs, cls=CustomJSONEncoder)
        return UploadResult(succeeded=len(success_rows), failed=len(failed_rows),
                            succeeded_items=list(success_rows))

