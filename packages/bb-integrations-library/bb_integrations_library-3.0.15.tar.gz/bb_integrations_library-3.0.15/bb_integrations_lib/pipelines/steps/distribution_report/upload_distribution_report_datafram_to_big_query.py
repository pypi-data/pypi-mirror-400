from typing import Dict, Tuple
import pandas as pd
from google.oauth2 import service_account
from loguru import logger
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.gcp.model import GoogleCredential
from bb_integrations_lib.util.utils import load_credentials
import pandas_gbq


class UploadDistributionReportToBigQuery(Step):
    def __init__(self, gbq_table_details: str, gbq_table_summary: str, google_project_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gbq_table_details = gbq_table_details
        self.gbq_table_summary = gbq_table_summary
        self.google_project_id = google_project_id

    def describe(self) -> str:
        return "Upload Distribution Report to GBQ"

    @property
    def credentials(self) -> GoogleCredential:
        return load_credentials(credential_type="google.credentials")

    async def execute(self, data: Tuple[pd.DataFrame, pd.DataFrame]) -> None:
        credentials = service_account.Credentials.from_service_account_info(self.credentials.model_dump())
        df_summary, df_detailed = data
        try:
            pandas_gbq.to_gbq(
                df_summary,
                destination_table=self.gbq_table_summary,
                project_id=self.google_project_id,
                if_exists='append',
                credentials=credentials,
            )
            pandas_gbq.to_gbq(
                df_detailed,
                destination_table='bb_reporting.contract_rack_util_product_detail',
                project_id=self.google_project_id,
                if_exists='append',
                credentials=credentials,
            )
        except Exception as e:
            logger.error(f"Failed to upload distribution report to BigQuery: {e}")
            raise e


