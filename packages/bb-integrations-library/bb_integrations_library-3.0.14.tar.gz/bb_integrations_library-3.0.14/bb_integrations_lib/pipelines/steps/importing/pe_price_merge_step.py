import json
from typing import List

from loguru import logger

from bb_integrations_lib.gravitate.pe_api import GravitatePEAPI
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult, UploadResult
from bb_integrations_lib.models.rita.issue import IssueBase, IssueCategory
from bb_integrations_lib.protocols.flat_file import PePriceMergeIntegration
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.util.utils import CustomJSONEncoder


class PEPriceMerge(Step):
    def __init__(
            self,
            pe_client: GravitatePEAPI,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pe_client = pe_client

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
                    response = await self.pe_client.merge_prices(row_dump)
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

