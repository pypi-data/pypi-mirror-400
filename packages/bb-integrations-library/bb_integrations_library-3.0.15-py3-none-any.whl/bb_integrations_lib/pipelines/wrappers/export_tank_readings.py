import csv
from datetime import datetime, UTC
from typing import Optional, Iterable, Self

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.pipelines.steps.export_dataframe_to_rawdata_step import ExportDataFrameToRawDataStep
from bb_integrations_lib.pipelines.steps.exporting.bbd_export_readings_step import BBDExportReadingsStep
from bb_integrations_lib.pipelines.steps.exporting.sftp_export_file_step import SFTPExportFileStep
from bb_integrations_lib.pipelines.steps.processing.bbd_format_tank_readings_step import ParseTankReadingsStep
from bb_integrations_lib.pipelines.steps.processing.tank_reading_touchup_steps import TRTouchUpStep
from bb_integrations_lib.pipelines.steps.send_attached_in_rita_email_step import SendAttachedInRitaEmailStep
from bb_integrations_lib.protocols.pipelines import JobPipeline
from bb_integrations_lib.secrets import SecretProvider
from bb_integrations_lib.secrets.factory import APIFactory
from bb_integrations_lib.shared.model import ExportReadingsConfig, FileFormat, ExportReadingsMultiConfig
from loguru import logger


class BBDReadingExportPipeline(JobPipeline):
    @classmethod
    async def create(
            cls,
            config: ExportReadingsConfig,
            secret_provider: SecretProvider,
            rita_client: GravitateRitaAPI,
            bucket_name: str,
            config_name: str,
            touchup_step: Optional[TRTouchUpStep] = None,
            file_date: Optional[datetime] = None,
            send_reports: bool = True
    ):
        api_factory = APIFactory(secret_provider)

        # Create clients
        sd_client = await api_factory.sd(config.sd_credentials)
        ims_database = await api_factory.mongo_db(config.ims_credentials)

        ftp_client = None
        if config.ftp_credentials and config.ftp_directory:
            ftp_client = await api_factory.ftp(config.ftp_credentials)

        file_date = file_date or datetime.now(UTC)
        file_name = f"{config.file_base_name}_{file_date.strftime(config.file_name_date_format)}.csv"

        steps = [
            {
                "id": "1",
                "parent_id": None,
                "step": BBDExportReadingsStep(
                    rita_client=rita_client,
                    sd_client=sd_client,
                    ims_database=ims_database,
                    reading_query=config.reading_query,
                    timezone=config.reading_reported_timezone,
                    window_mode=config.window_mode,
                    hours_back=config.hours_back,
                )
            },
            {
                "id": "2",
                "parent_id": "1",
                "step": ParseTankReadingsStep(
                    file_format=config.file_format,
                    timezone=config.reading_reported_timezone,
                    include_water_level=config.include_water_level,
                    disconnected_column=config.disconnected_column,
                    disconnected_only=config.disconnected_only,
                    disconnected_hours_threshold=config.disconnected_hours_threshold,
                )
            },
        ]

        if touchup_step is not None:
            steps.append({
                "id": "touchup",
                "parent_id": "2",
                "step": touchup_step,
            })
            final_build_step = "touchup"
        else:
            final_build_step = "2"

        pd_export_function = "write_csv" if config.use_polars else "to_csv"
        if config.use_polars:
            pd_kwargs: dict = {"include_header": True}
            if config.file_format == FileFormat.reduced:
                pd_kwargs["quote_style"] = "never"
        else:
            pd_kwargs = {"header": True, "index": False}
            if config.file_format == FileFormat.reduced:
                pd_kwargs["quoting"] = csv.QUOTE_NONE
                pd_kwargs["escapechar"] = "\\"

        steps.append({
            "id": "3",
            "parent_id": final_build_step,
            "step": ExportDataFrameToRawDataStep(
                pandas_export_function=pd_export_function,
                pandas_export_kwargs=pd_kwargs,
                file_name=file_name,
            )
        })

        if config.ftp_directory is not None and ftp_client is not None:
            steps.append({
                "id": "4",
                "parent_id": "3",
                "step": SFTPExportFileStep(
                    ftp_client=ftp_client,
                    ftp_destination_dir=config.ftp_directory,
                )
            })

        if config.email_addresses is not None:
            steps.append({
                "id": "send_email",
                "parent_id": "3",
                "step": SendAttachedInRitaEmailStep(
                    rita_client=rita_client,
                    to=config.email_addresses,
                    html_content="Tank Reading Export",
                    subject=f"Gravitate Tank Reading Export - {datetime.now().isoformat()}",
                    timeout=30.0,
                )
            })

        config = await rita_client.get_config_by_name(bucket_path="/" + bucket_name, config_name=config_name)
        config_id = config[config_name].config_id
        return cls(
            steps,
            rita_client=rita_client,
            pipeline_name=f"Import tank readings - {config_name}",
            pipeline_config_id=config_id,
            secret_provider=secret_provider,
            send_reports=send_reports
        )

class MultiExportTankReadingsPipeline:
    def __init__(self, pipelines: Iterable[BBDReadingExportPipeline]):
        self.pipelines = pipelines

    @classmethod
    async def create(cls, config_id: str, rita_client: GravitateRitaAPI,
                     secret_provider: SecretProvider, send_reports: bool = True) -> Self:
        main_config = await rita_client.get_config_by_id(config_id)
        [bucket] = [b for b in await rita_client.get_all_buckets() if b["_id"] == main_config.owning_bucket_id]

        multi_export_config = ExportReadingsMultiConfig.model_validate(main_config.config)
        pipelines = []
        for export_config in multi_export_config.configs:
            for config_name in export_config.config_names:
                logger.info(f"Creating pipeline for config {config_name}")
                pipelines.append(await BBDReadingExportPipeline.create(
                    config=export_config,
                    secret_provider=secret_provider,
                    rita_client=rita_client,
                    bucket_name=bucket["name"],
                    config_name=config_name,
                    send_reports=send_reports,
                ))
        return cls(pipelines)

    async def run(self) -> None:
        if not self.pipelines:
            raise Exception("No pipelines to run - check config and try again")
        for pipeline in self.pipelines:
            try:
                logger.info(f"Starting pipeline '{pipeline.pipeline_name}'")
                await pipeline.execute()
                logger.info(f"Finished pipeline '{pipeline.pipeline_name}'")
                logger.info("-" * 40)
            except Exception as e:
                logger.exception(f"Failed to run pipeline '{pipeline.pipeline_name}'")
