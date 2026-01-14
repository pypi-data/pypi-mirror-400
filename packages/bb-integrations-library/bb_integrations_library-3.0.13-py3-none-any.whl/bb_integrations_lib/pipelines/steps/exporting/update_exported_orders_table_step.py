import uuid
from datetime import datetime, UTC

from google.cloud import bigquery
from google.oauth2 import service_account
from loguru import logger

from bb_integrations_lib.models.pipeline_structs import BolExportResults
from bb_integrations_lib.protocols.pipelines import Step


class UpdateExportedOrdersTableStep(Step[BolExportResults, BolExportResults, None]):
    def __init__(self, step_configuration):
        super().__init__(step_configuration)
        self.exported_order_table_name = step_configuration["exported_order_table_name"]
        self.exported_order_errors_table_name = step_configuration["exported_order_errors_table_name"]
        self.project_id = step_configuration["project_id"]
        self.gcp_credentials_file = step_configuration["gcp_credentials_file"]
        if not self.gcp_credentials_file.endswith(".json"):
            self.gcp_credentials_file += ".json"

    def describe(self) -> str:
        return "Update the GCP bigquery table to include the newly-exported orders"

    async def execute(self, results: BolExportResults) -> BolExportResults:
        orders = results.orders
        unique_order_numbers_exported = set(x[results.order_number_key] for x in orders)
        now = datetime.now(UTC).isoformat().split("+")[0]
        credentials = service_account.Credentials.from_service_account_file(self.gcp_credentials_file)
        if len(unique_order_numbers_exported) > 0:
            to_insert = [{
                "file_name": results.file_name,
                "date": now,
                "order_number": x
            } for x in unique_order_numbers_exported]
            logger.debug(f"Inserting {len(to_insert)} records for run {results.file_name}")
            client = bigquery.Client(credentials=credentials)
            gbq_errors = client.insert_rows_json(self.exported_order_table_name, to_insert)
            if gbq_errors:
                logger.error(gbq_errors)
            else:
                logger.debug(f"Updated {self.exported_order_table_name}")
        else:
            logger.debug("No exported orders to insert.")

        errors_insert = [{
            "id": str(uuid.uuid4()),
            "export_id": results.file_name,
            "order_number": str(x["order_number"]),
            "error": x["error"],
            "date": now
        } for x in results.errors]
        if len(errors_insert) > 0:
            logger.debug(f"Inserting {len(errors_insert)} records for run {results.file_name}")
            client = bigquery.Client(credentials=credentials)
            gbq_errors = client.insert_rows_json(self.exported_order_errors_table_name, errors_insert)
            if gbq_errors:
                logger.error(gbq_errors)
            else:
                logger.debug(f"Updated {self.exported_order_errors_table_name}")
        else:
            logger.debug(f"No errors to insert.")

        return results
