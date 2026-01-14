from datetime import datetime

from pymongo import AsyncMongoClient

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.pipelines.parsers.distribution_report.order_by_site_product_parser import \
    OrderBySiteProductParser
from bb_integrations_lib.pipelines.parsers.distribution_report.tank_configs_parser import TankConfigsParser
from bb_integrations_lib.pipelines.steps.distribution_report import DistributionReportDfToRawData, GetModelHistoryStep, \
    GetOrderBySiteProductStep, GetTankConfigsStep, JoinDistributionOrderDosStep, UploadDistributionReportToBigQuery
from bb_integrations_lib.pipelines.steps.exporting.sftp_export_file_step import SFTPExportFileStep
from bb_integrations_lib.pipelines.steps.send_attached_in_rita_email_step import SendAttachedInRitaEmailStep
from bb_integrations_lib.protocols.pipelines import JobPipeline
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.shared.model import DistributionReportConfig


class DistributionReportPipeline(JobPipeline):
    @classmethod
    async def create(
            cls,
            config_id: str,
            rita_client: GravitateRitaAPI,
            sd_client: GravitateSDAPI,
            ims_database: AsyncMongoClient,
            client_name: str,
            ftp_client: FTPIntegrationClient | None = None,
    ):
        config = await rita_client.get_config_by_id(config_id)
        job_config = DistributionReportConfig.model_validate(config.config)

        steps = [
            {
                "id": "get_model_history",
                "parent_id": None,
                "step": GetModelHistoryStep(
                    mongo_database=ims_database,
                    n_hours_back=job_config.n_hours_back,
                    include_model_mode=job_config.include_model_mode,
                    state=job_config.order_state,
                )
            },
            {
                "id": "get_tank_config",
                "parent_id": "get_model_history",
                "step": GetTankConfigsStep(
                    mongo_database=ims_database,
                    parser=TankConfigsParser
                ),
            },
            {
                "id": "get_orders",
                "parent_id": "get_model_history",
                "step":
                    GetOrderBySiteProductStep(
                        sd_client=sd_client,
                        parser=OrderBySiteProductParser,
                        include_model_mode=job_config.include_model_mode,
                    )
            },
            {
                "id": "join_df",
                "parent_id": "get_orders",
                "alt_input": "get_model_history",
                "step":
                    JoinDistributionOrderDosStep(
                        client_name=client_name,
                    )
            },
            {
                "id": "upload_to_gbq",
                "parent_id": "join_df",
                "step":
                    UploadDistributionReportToBigQuery(
                        google_project_id=job_config.google_project_id,
                        gbq_table_summary=job_config.gbq_table_summary,
                        gbq_table_details=job_config.gbq_table_details,
                    )
            }
        ]
        if job_config.ftp_directory is not None or job_config.email_addresses is not None:
            steps.append({
                "id": "df_to_raw_data",
                "parent_id": "join_df",
                "step":
                    DistributionReportDfToRawData(
                        file_base_name=job_config.file_base_name,
                        file_name_date_format=job_config.file_name_date_format,
                    )

            })
        if job_config.ftp_directory is not None:
            steps.append({
                "id": "upload_to_ftp",
                "parent_id": "df_to_raw_data",
                "step": SFTPExportFileStep(
                    ftp_client=ftp_client,
                    ftp_destination_dir=job_config.ftp_directory,
                )
            })
        if job_config.email_addresses is not None:
            steps.append({
                "id": "send_email",
                "parent_id": "df_to_raw_data",
                "step": SendAttachedInRitaEmailStep(
                    rita_client=rita_client,
                    to=job_config.email_addresses,
                    html_content="Distribution Report",
                    subject=f"Gravitate Distribution Report - {datetime.now().isoformat()}",
                    use_extension=False,
                )
            })

        return
