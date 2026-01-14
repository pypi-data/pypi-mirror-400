from datetime import datetime, timedelta
from typing import Iterable, Self

import pytz
from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.mappers.rita_mapper import RitaAPICachedMappingProvider
from bb_integrations_lib.pipelines.parsers.tank_reading_parser import TankReadingParser
from bb_integrations_lib.pipelines.steps.importing.load_imap_attachment_step import LoadIMAPAttachmentStep
from bb_integrations_lib.pipelines.steps.importing.sftp_file_config_step import SFTPFileConfigStep
from bb_integrations_lib.pipelines.steps.null_step import NullStep
from bb_integrations_lib.pipelines.steps.processing.archive_gcs_step import ArchiveGCSStep
from bb_integrations_lib.pipelines.steps.processing.archive_sftp_step import ArchiveSFTPStep
from bb_integrations_lib.pipelines.steps.processing.bbd_upload_tankreading_step import BBDUploadTankReadingStep
from bb_integrations_lib.pipelines.steps.processing.delete_sftp_step import DeleteSFTPStep
from bb_integrations_lib.pipelines.steps.processing.file_config_parser_step_v2 import FileConfigParserV2
from bb_integrations_lib.protocols.pipelines import JobPipeline
from bb_integrations_lib.secrets import SecretProvider
from bb_integrations_lib.secrets.factory import APIFactory
from bb_integrations_lib.shared.model import ImportTankReadings, ATGConfig, ConfigMode
from loguru import logger


class BBDImportTankReadingsPipeline(JobPipeline):
    @classmethod
    async def create(
            cls,
            config: ATGConfig,
            secret_provider: SecretProvider,
            rita_client: GravitateRitaAPI,
            bucket_name: str,
            config_name: str,
            tenant_name: str,
            send_reports: bool = True
    ):
        api_factory = APIFactory(secret_provider)

        steps = [{
            "id": "start",
            "parent_id": None,
            "step": NullStep({})
        }]
        if config.minutes_back is not None and config.timezone is not None:
            min_date = datetime.now(pytz.timezone(config.timezone)) - timedelta(minutes=config.minutes_back)
        else:
            min_date = None

        ftp_client = None
        if config.mode == "ftp":
            ftp_client = await api_factory.ftp(config.ftp_credentials)
            pull_step = SFTPFileConfigStep(
                rita_client=rita_client,
                ftp_client=ftp_client,
                bucket_name=bucket_name,
                config_name=config_name,
                mode=ConfigMode.ByName,
                match_mode=config.file_match_type,
                min_date=min_date or datetime.min
            )
        elif config.mode == "email":
            pull_step = LoadIMAPAttachmentStep(
                rita_client=rita_client,
                imap_client=await api_factory.imap(config.email_credentials),
                from_email_address=config.from_email_address,
                delivered_to_email_address=config.delivered_to_email_address,
                to_email_address=config.to_email_address,
                attachment_extension=config.attachment_extension or ".csv",
                bucket_name=bucket_name,
                config_names=[config_name],
                email_subject=config.email_subject
            )
        else:
            raise ValueError(f"Invalid mode: {config.mode}")

        mapping_provider = RitaAPICachedMappingProvider(rita_client)

        steps += [
            {
                "id": "pull",
                "parent_id": "start",
                "step": pull_step
            },
            {
                "id": f"parse_readings",
                "parent_id": "pull",
                "step": FileConfigParserV2(
                    rita_client=rita_client,
                    mapping_type=config.mapping_type,
                    parser=TankReadingParser,
                    parser_kwargs={
                        "included_payload": {
                            "source": f"{tenant_name} flat file tank readings"
                        },
                        "mapping_provider": mapping_provider,
                        "sd_client": await api_factory.sd(config.sd_credentials),
                    }
                )
            },
            {
                "id": f"bbd_upload",
                "parent_id": f"parse_readings",
                "step": BBDUploadTankReadingStep(
                    sd_client=await api_factory.sd(config.sd_credentials),
                )
            },
        ]
        if config.archive_gcs_bucket_path is not None and config.gcs_credentials is not None:
            steps.append({
                "id": f"archive_gcs",
                "parent_id": f"bbd_upload",
                "alt_input": "pull",
                "step": ArchiveGCSStep(
                    gcloud_storage=await api_factory.gcloud_storage(config.gcs_credentials),
                    bucket_path=config.archive_gcs_bucket_path,
                )
            })
        if config.archive_files:
            if ftp_client:
                steps.append({
                    "id": f"archive_ftp",
                    "parent_id": f"bbd_upload",
                    "alt_input": "pull",
                    "step": ArchiveSFTPStep(
                        ftp_client=ftp_client,
                    )
                })
            else:
                logger.warning("No FTP credentials provided, skipping FTP archive step")
        if config.delete_files:
            if ftp_client:
                steps.append({
                    "id": "delete_ftp",
                    "parent_id": f"bbd_upload",
                    "alt_input": "pull",
                    "step": DeleteSFTPStep(
                        ftp_client=ftp_client
                    )
                })
            else:
                logger.warning("No FTP credentials provided, skipping FTP delete step")
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


class MultiImportTankReadingsPipeline:
    def __init__(self, pipelines: Iterable[BBDImportTankReadingsPipeline]):
        self.pipelines = pipelines

    @classmethod
    async def create(cls, config_id: str, tenant_name: str, rita_client: GravitateRitaAPI,
                     secret_provider: SecretProvider, send_reports: bool = True) -> Self:
        main_config = await rita_client.get_config_by_id(config_id)
        [bucket] = [b for b in await rita_client.get_all_buckets() if b["_id"] == main_config.owning_bucket_id]

        import_config = ImportTankReadings.model_validate(main_config.config)
        pipelines = []
        for atg_config in import_config.configs:
            for config_name in atg_config.config_names:
                logger.info(f"Creating pipeline for config {config_name}")
                pipelines.append(await BBDImportTankReadingsPipeline.create(
                    config=atg_config,
                    secret_provider=secret_provider,
                    rita_client=rita_client,
                    bucket_name=bucket["name"],
                    config_name=config_name,
                    tenant_name=tenant_name,
                    send_reports=send_reports
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
