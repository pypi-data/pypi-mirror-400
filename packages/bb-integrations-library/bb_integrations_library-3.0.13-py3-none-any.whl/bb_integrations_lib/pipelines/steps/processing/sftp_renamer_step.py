import os
from asyncio import sleep
from datetime import UTC, datetime

import loguru

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.pipeline_structs import StopPipeline
from bb_integrations_lib.models.rita.config import Config
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient


class SFTPRenamerStep(Step):
    def __init__(self, rita_client: GravitateRitaAPI, ftp_client: FTPIntegrationClient, config_id: str,
                 halt_early: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.ftp_client = ftp_client
        self.config_id = config_id
        self.halt_early = halt_early

        self.config: Config | None = None
        self.directory: str | None = None
        self.file_name: str | None = None
        self.output_name_base: str | None = None

    async def load_config(self):
        self.config = await self.rita_client.get_config_by_id(self.config_id)
        self.directory = self.config.config.get("directory")

        if not self.directory:
            raise ValueError("The provided config is missing the `directory` field.")
        self.file_name = self.config.config.get("file_name")
        if not self.file_name:
            raise ValueError("The provided config is missing the `file_name` field.")
        self.output_name_base = self.config.config.get("output_name_base")
        if not self.output_name_base:
            raise ValueError("The provided config is missing the `output_name_base` field.")

    def describe(self) -> str:
        return "Rename files in FTP directory."

    async def execute(self, i: None) -> None:
        await self.load_config()

        filenames = self.ftp_client.list_files(self.directory)
        found_any = False
        for filename in filenames:
            if self.file_name in filename:
                found_any = True
                file_extension = os.path.splitext(filename)[1]
                date = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
                new_filename = f"{self.output_name_base}{date}.{file_extension}"
                old = os.path.join(self.directory, filename)
                new = os.path.join(self.directory, new_filename)
                self.ftp_client.rename_file(old, new)
                loguru.logger.info(f"File renamed: {old} -> {new}")
                await sleep(1)
        if not found_any and self.halt_early:
            raise StopPipeline("No files to rename.")
