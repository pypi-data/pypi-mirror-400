from loguru import logger

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.pipeline_structs import BBDUploadResult
from bb_integrations_lib.models.rita.audit import ProcessReportV2Status, CreateReportV2, UploadProcessReportFile
from bb_integrations_lib.protocols.pipelines import Step


class SendProcessReportStep(Step):
    def __init__(self, rita_client: GravitateRitaAPI, trigger: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.trigger = trigger

    def describe(self) -> str:
        if self.pipeline_context.file_config is not None:
            return "Upload process report to file config " + self.pipeline_context.file_config.client_name
        else:
            raise RuntimeError("Attempting to use SendProcessReportStep without a previous step setting the file_config")

    async def execute(self, i: BBDUploadResult) -> BBDUploadResult:
        fc = self.pipeline_context.file_config
        if fc is None or fc.config_id is None:
            raise RuntimeError("Attempting to use SendProcessReportStep but the fileconfig is either not available from context, or does not have its config_id set.")
        logger.info("Uploading process report to RITA...")
        try:
            await self.rita_client.create_process_report(CreateReportV2(
                trigger=self.trigger,
                # If we would be creating an error report, the exception is caught and reporting happens in finish_pipeline
                status=ProcessReportV2Status.stop,
                config_id=self.pipeline_context.file_config.config_id,
                # Logs are one list item per line, newlines already included. Join into one string.
                log=UploadProcessReportFile(file_base_name=f"log", content="".join(self.pipeline_context.logs)),
                included_files = [
                    UploadProcessReportFile(file_base_name=name, content=content)
                    for name, content in self.pipeline_context.included_files.items()
                ]
            ))
            logger.info("Uploaded.")
        except Exception as e:
            logger.warning("Failed to upload process report.")

        # Reset logs for use by the next branch, if the pipeline has one.
        self.pipeline_context.logs = []
        self.pipeline_context.included_files = {}

        return i
