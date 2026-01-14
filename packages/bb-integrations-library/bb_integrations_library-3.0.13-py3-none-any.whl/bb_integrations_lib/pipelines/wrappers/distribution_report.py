from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bb_integrations_lib.models.pipeline_structs import PipelineProcessReportConfig
from bb_integrations_lib.pipelines.parsers.distribution_report.order_by_site_product_parser import \
    OrderBySiteProductParser
from bb_integrations_lib.pipelines.parsers.distribution_report.tank_configs_parser import TankConfigsParser
from bb_integrations_lib.pipelines.steps.distribution_report.distribution_report_datafram_to_raw_data import \
    DistributionReportDfToRawData
from bb_integrations_lib.pipelines.steps.distribution_report.get_model_history_step import GetModelHistoryStep
from bb_integrations_lib.pipelines.steps.distribution_report.get_order_by_site_product_step import \
    GetOrderBySiteProductStep
from bb_integrations_lib.pipelines.steps.distribution_report.get_tank_configs_step import GetTankConfigsStep
from bb_integrations_lib.pipelines.steps.distribution_report.join_distribution_order_dos_step import \
    JoinDistributionOrderDosStep
from bb_integrations_lib.pipelines.steps.distribution_report.upload_distribution_report_datafram_to_big_query import \
    UploadDistributionReportToBigQuery
from bb_integrations_lib.pipelines.steps.exporting.sftp_export_file_step import SFTPExportFileStep
from bb_integrations_lib.pipelines.steps.send_attached_in_rita_email_step import SendAttachedInRitaEmailStep
from bb_integrations_lib.pipelines.wrappers.wrapper import PipelineWrapper
from bb_integrations_lib.protocols.pipelines import JobPipeline
from bb_integrations_lib.shared.model import DistributionReportConfig
from bb_integrations_lib.util.config.model import GlobalConfig
from loguru import logger


class DistributionReportPipeline(JobPipeline):
    def __init__(self,
                 tenant_name: str,
                 pipeline_config_id: str,
                 config_name: str,
                 secret_data: GlobalConfig,
                 config: DistributionReportConfig,
                 mode: str = "test",
                 ftp_creds: Optional[str] = None,
                 sd_basic_auth: bool = False,
                 ):
        self.mode = mode
        self.tenant_name = tenant_name
        self.config = config
        self.config_id = pipeline_config_id
        self.config_name = config_name
        self.secret_data = secret_data
        self.ftp_creds = ftp_creds
        self.process_report_config = PipelineProcessReportConfig(
            config_id=self.config_id,
            trigger=self.config_name,
        )
        steps = [
            {
                "id": "get_model_history",
                "parent_id": None,
                "step": GetModelHistoryStep({
                    "tenant_name": self.tenant_name,
                    "mode": self.mode,
                    "n_hours_back": self.config.n_hours_back,
                    "include_model_mode": self.config.include_model_mode,
                    "state": self.config.order_state,
                })
            },
            {
                "id": "get_tank_config",
                "parent_id": "get_model_history",
                "step": GetTankConfigsStep({
                    "tenant_name": self.tenant_name,
                    "mode": self.mode,
                    "parser": TankConfigsParser
                }),
            },
            {
                "id": "get_orders",
                "parent_id": "get_model_history",
                "step":
                    GetOrderBySiteProductStep({
                        "tenant_name": self.tenant_name,
                        "mode": self.mode,
                        "parser": OrderBySiteProductParser,
                        "include_model_mode": self.config.include_model_mode,
                        "sd_basic_auth": sd_basic_auth,
                    })
            },
            {
                "id": "join_df",
                "parent_id": "get_orders",
                "alt_input": "get_model_history",
                "step":
                    JoinDistributionOrderDosStep({
                        "tenant_name": self.tenant_name,
                    })
            },
            {
                "id": "upload_to_gbq",
                "parent_id": "join_df",
                "step":
                    UploadDistributionReportToBigQuery({
                        "google_project_id": self.config.google_project_id,
                        "gbq_table_summary": self.config.gbq_table_summary,
                        "gbq_table_details": self.config.gbq_table_details,
                    })

            }
        ]
        if self.config.ftp_directory is not None or self.config.email_addresses is not None:
            steps.append({
                "id": "df_to_raw_data",
                "parent_id": "join_df",
                "step":
                    DistributionReportDfToRawData({
                        "tenant_name": self.tenant_name,
                        "file_base_name": self.config.file_base_name,
                        "file_name_date_format": self.config.file_name_date_format,
                    })

            })
        if self.config.ftp_directory is not None:
            steps.append({
                "id": "upload_to_ftp",
                "parent_id": "df_to_raw_data",
                "step": SFTPExportFileStep({
                    "ftp_creds": self.ftp_creds,
                    "sftp_destination_dir": self.config.ftp_directory,
                })
            })
        if self.config.email_addresses is not None:
            steps.append({
                "id": "send_email",
                "parent_id": "df_to_raw_data",
                "step": SendAttachedInRitaEmailStep({
                    "base_url": "https://rita.gravitate.energy",
                    "client_id": self.secret_data.prod.rita.client_id,
                    "client_secret": self.secret_data.prod.rita.client_secret,
                    "rita_tenant": self.tenant_name,
                    "to": self.config.email_addresses,
                    "html_content": "Distribution Report",
                    "subject": f"Gravitate Distribution Report - {datetime.now().isoformat()}",
                    "use_extension": False,
                })
            })
        super().__init__(steps, initial_input=None, catch_step_errors=True,
                         process_report_config=self.process_report_config)


class CreateDistributionReportPipeline(PipelineWrapper):
    def __init__(self,
                 tenant_name: str,
                 bucket_name: str,
                 run_mode: str,
                 config_class=DistributionReportConfig,
                 ftp_creds: Optional[str] = None,
                 sd_basic_auth: bool = False,
                 ):
        self.tenant_name = tenant_name
        self.bucket_name = bucket_name
        self.mode = run_mode
        self.ftp_creds = ftp_creds
        self.sd_basic_auth = sd_basic_auth
        super().__init__(
            tenant_name=tenant_name,
            bucket_name=bucket_name,
            config_class=config_class,
            mode=run_mode
        )

    async def create(self, config_name: str) -> DistributionReportPipeline:
        config, config_id, name = await self.load_config(config_name)
        logger.info(
            f"Loaded config for tenant '{self.tenant_name}' with name '{name}': {config.model_dump()}"
        )
        return DistributionReportPipeline(
            tenant_name=self.tenant_name,
            config=config,
            pipeline_config_id=config_id,
            secret_data=self.secret_data,
            config_name=name,
            mode=self.mode,
            ftp_creds=self.ftp_creds,
            sd_basic_auth=self.sd_basic_auth
        )

    async def run(self, base: str = "Distribution Report"):
        config_name = f"{self.tenant_name} - {base}"
        try:
            logger.info(f"Starting distribution report pipeline for tenant '{self.tenant_name}' with config '{config_name}'")
            pipeline = await self.create(config_name)
            await pipeline.execute()
            logger.info(f"Completed pipeline for client: {self.tenant_name}")
            return f"Success: {self.tenant_name}"
        except Exception as e:
            logger.error(
                f"Failed to run import pipeline for client '{self.tenant_name}' with config '{config_name}': {e}")
            return f"Error: {self.tenant_name} - {str(e)}"