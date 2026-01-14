import asyncio
import csv
from datetime import datetime, UTC
from typing import Optional, List, Dict, Union
from loguru import logger

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.pipeline_structs import PipelineProcessReportConfig
from bb_integrations_lib.pipelines.steps.export_dataframe_to_rawdata_step import ExportDataFrameToRawDataStep
from bb_integrations_lib.pipelines.steps.exporting.bbd_export_readings_step import BBDExportReadingsStep
from bb_integrations_lib.pipelines.steps.exporting.sftp_export_file_step import SFTPExportFileStep
from bb_integrations_lib.pipelines.steps.processing.bbd_format_tank_readings_step import ParseTankReadingsStep
from bb_integrations_lib.pipelines.steps.processing.tank_reading_touchup_steps import TRTouchUpStep
from bb_integrations_lib.pipelines.steps.send_attached_in_rita_email_step import SendAttachedInRitaEmailStep
from bb_integrations_lib.pipelines.wrappers.wrapper import PipelineWrapper
from bb_integrations_lib.protocols.pipelines import JobPipeline, Step
from bb_integrations_lib.shared.model import ExportReadingsConfig, FileFormat
from bb_integrations_lib.util.config.manager import GlobalConfigManager
from bb_integrations_lib.util.config.model import GlobalConfig


class BBDReadingExportPipeline(JobPipeline):
    def __init__(
            self,
            rita_tenant_name: str,
            config: ExportReadingsConfig,
            pipeline_config_id: str,
            secret_data: GlobalConfig,
            config_name: str,
            ftp_creds: str,
            mode: str,
            touchup_step: TRTouchUpStep,
            file_date: Optional[datetime] = None,
            use_polars: bool = False,
    ):
        self.mode = mode
        self.tenant_name = rita_tenant_name
        self.config_id = pipeline_config_id
        self.config = config
        self.secret_data = secret_data
        self.config_name = config_name
        self.ftp_creds = ftp_creds
        self.touchup_step = touchup_step
        self.file_date = file_date or datetime.now(UTC)
        self.file_name = f"{self.config.file_base_name}_{self.file_date.strftime(config.file_name_date_format)}.csv"
        self.use_polars = use_polars

        self.process_report_config = PipelineProcessReportConfig(
            config_id=self.config_id,
            trigger=self.config_name,
        )
        steps = [
            {
                "id": "1",
                "parent_id": None,
                "step": BBDExportReadingsStep({
                    "tenant_name": self.tenant_name,
                    "readings_query": self.config.reading_query.model_dump(),
                    "hours_back": self.config.hours_back,
                    "window_mode": self.config.window_mode,
                    "timezone": self.config.reading_reported_timezone
                })
            },
            {
                "id": "2",
                "parent_id": "1",
                "step": ParseTankReadingsStep({
                    "format": self.config.file_format,
                    "timezone": self.config.reading_reported_timezone,
                    "include_water_level": self.config.include_water_level,
                    "disconnected_column": self.config.disconnected_column,
                    "disconnected_only": self.config.disconnected_only,
                    "disconnected_hours_threshold": self.config.disconnected_hours_threshold,
                })
            },
        ]
        if self.touchup_step is not None:
            steps.append({
                "id": "touchup",
                "parent_id": "2",
                "step": self.touchup_step,
            })
            final_build_step = "touchup"
        else:
            final_build_step = "2"
        pd_export_function = "write_csv" if self.use_polars else "to_csv"
        if self.use_polars:
            pd_kwargs = {"include_header": True}
            if self.config.file_format == FileFormat.reduced:
                pd_kwargs["quote_style"] = "never"
        else:
            pd_kwargs = {"header": True, "index": False}
            if self.config.file_format == FileFormat.reduced:
                pd_kwargs["quoting"] = csv.QUOTE_NONE
                pd_kwargs["escapechar"] = "\\"

        steps.append({
            "id": "3",
            "parent_id": final_build_step,
            "step": ExportDataFrameToRawDataStep({
                "pandas_export_function": pd_export_function,
                "pandas_export_kwargs": pd_kwargs,
                "file_name": self.file_name
            })
        })

        if self.config.ftp_directory is not None:
            steps.append({
                "id": "4",
                "parent_id": "3",
                "step": SFTPExportFileStep({
                    "ftp_creds": self.ftp_creds,
                    "sftp_destination_dir": self.config.ftp_directory,
                })
            })
        if self.config.email_addresses is not None:
            steps.append({
                "id": "send_email",
                "parent_id": "3",
                "step": SendAttachedInRitaEmailStep({
                    "base_url": "https://rita.gravitate.energy",
                    "client_id": self.secret_data.prod.rita.client_id,
                    "client_secret": self.secret_data.prod.rita.client_secret,
                    "rita_tenant": self.tenant_name,
                    "to": self.config.email_addresses,
                    "html_content": "Tank Reading Export",
                    "subject": f"Gravitate Tank Reading Export - {datetime.now().isoformat()}",
                    "timeout": 30.0,
                    "use_extension": True
                })
            })
        super().__init__(steps, None, catch_step_errors=True, process_report_config=self.process_report_config)


class CreateExportReadingPipeline(PipelineWrapper):
    def __init__(self,
                 tenant_name: str,
                 bucket_name: str,
                 config_class=ExportReadingsConfig,
                 ftp_creds: Optional[str] = None,
                 mode: str = "production",
                 touchup_step: Optional[TRTouchUpStep] = None,
                 file_date_override: Optional[datetime] = None,
                 use_polars: bool = False,
                 ) -> None:
        self.mode = mode
        self.ftp_creds = ftp_creds
        self.touchup_step = touchup_step
        self.file_date_override = file_date_override
        self.use_polars = use_polars
        super().__init__(
            tenant_name=tenant_name,
            bucket_name=bucket_name,
            config_class=config_class
        )

    async def create(self, config_name: str, client_ftp_creds: Optional[str] = None) -> BBDReadingExportPipeline:
        """Create a pipeline instance for a specific config name."""
        config, config_id, name = await self.load_config(config_name)
        logger.info(
            f"Loaded config for tenant '{self.tenant_name}' with name '{name}': {config.model_dump()}"
        )

        # Determine FTP credentials to use (priority: client-specific > instance-level > config)
        ftp_creds = client_ftp_creds or self.ftp_creds or config.ftp_credentials

        if client_ftp_creds:
            logger.info(f"Using client-specific FTP credentials for config '{config_name}'")
        elif self.ftp_creds:
            logger.info(f"Using instance-level FTP credentials for config '{config_name}'")
        else:
            logger.info(f"Using config-level FTP credentials for config '{config_name}'")

        return BBDReadingExportPipeline(
            rita_tenant_name=self.tenant_name,
            config=config,
            pipeline_config_id=config_id,
            secret_data=self.secret_data,
            config_name=name,
            ftp_creds=ftp_creds,
            mode=self.mode,
            touchup_step=self.touchup_step,
            file_date=self.file_date_override,
            use_polars=self.use_polars,
        )

    async def run_for_client(self, client_name: str, base: str = "ATG Readings Export",
                             client_ftp_creds: Optional[str] = None):
        """Run pipeline for a specific client with optional custom FTP credentials."""
        config_name = f"{self.tenant_name} - {client_name} {base}"
        try:
            logger.info(f"Starting export pipeline for client '{client_name}' with config '{config_name}'")
            pipeline = await self.create(config_name, client_ftp_creds)
            await pipeline.execute()
            logger.info(f"Completed pipeline for client: {client_name}")
            return f"Success: {client_name}"
        except Exception as e:
            logger.error(f"Failed to run export pipeline for client '{client_name}' with config '{config_name}': {e}")
            return f"Error: {client_name} - {str(e)}"

    async def run_pipeline_with_delay(self, client_name: str, delay: int, base: str = "ATG Readings Export",
                                      client_ftp_creds: Optional[str] = None):
        """Run pipeline for a client with a delay."""
        if delay > 0:
            logger.info(f"Waiting {delay} seconds before starting pipeline for client: {client_name}")
            await asyncio.sleep(delay)
        return await self.run_for_client(client_name, base, client_ftp_creds)

    async def run_for_many_clients(self, clients: Union[List[str], Dict[str, str]],
                                   base: str = "ATG Readings Export"):
        """
        Run pipelines for multiple clients with staggered delays.

        Args:
            clients: Either a list of client names or a dict mapping client names to FTP credentials
            base: Base name for config lookup
        """
        # Handle both list and dict formats
        if isinstance(clients, dict):
            client_names = list(clients.keys())
            tasks = [
                self.run_pipeline_with_delay(client, i * 3, base, clients.get(client))
                for i, client in enumerate(client_names)
            ]
        else:
            client_names = clients
            tasks = [
                self.run_pipeline_with_delay(client, i * 3, base)
                for i, client in enumerate(client_names)
            ]

        logger.info(f"Starting {len(tasks)} pipeline tasks for clients: {client_names}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Results:")
        for client, result in zip(client_names, results):
            logger.info(f"{client}: {result}")
        return results
