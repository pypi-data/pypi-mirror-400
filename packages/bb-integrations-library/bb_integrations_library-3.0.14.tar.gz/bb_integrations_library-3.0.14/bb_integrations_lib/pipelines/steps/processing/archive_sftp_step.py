import os
import uuid
from typing import Any

import loguru

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.shared.model import FileConfigRawData, RawData


class ArchiveSFTPStep(Step):
    def __init__(self, ftp_client: FTPIntegrationClient, src_directory: str | None = None,
                 archive_directory: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ftp_client = ftp_client
        self.src_directory = src_directory
        self.archive_directory = archive_directory

    def describe(self) -> str:
        return "SFTP Rename Step"

    async def execute(self, i: Any) -> Any:
        if isinstance(i, FileConfigRawData):
            old_name = os.path.join(i.file_config.inbound_directory, i.file_name)
            new_name = os.path.join(i.file_config.archive_directory, i.file_name)
        elif isinstance(i, RawData):
            if self.src_directory is None or self.archive_directory is None:
                raise RuntimeError("Attempted to archive with a RawData object but src_directory or archive_directory was not provided.")
            old_name = os.path.join(self.src_directory, i.file_name)
            new_name = os.path.join(self.archive_directory, i.file_name)
        else:
            raise NotImplementedError(f"Unsupported input type: {type(i)}")
        try:
            loguru.logger.debug(f"Archiving file {old_name} -> {new_name}")
            self.ftp_client.rename_file(old_name, new_name)
        except Exception as e:
            try:
                loguru.logger.debug(f"Archiving file failed...")
                # this file may already exist. Give the file a randomized name and then archive.
                new_name = new_name.replace(i.file_name, f"DUPLICATE_{uuid.uuid4()}_{i.file_name}")
                loguru.logger.debug(f"Archiving file (backup attempt) {old_name} -> {new_name}")
                self.ftp_client.rename_file(old_name, new_name)
            except:
                loguru.logger.warning(f"Archiving backup file failed. Deleting source file to prevent duplicate readings.")
                self.ftp_client.delete_file(old_name)
        loguru.logger.debug(f"Archived file {old_name} -> {new_name}")
        return i