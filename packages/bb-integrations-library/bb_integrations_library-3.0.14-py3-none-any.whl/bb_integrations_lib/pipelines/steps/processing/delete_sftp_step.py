import os
from typing import Dict, Any

import loguru

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.shared.model import FileConfigRawData, RawData


class DeleteSFTPStep(Step):
    def __init__(self, ftp_client: FTPIntegrationClient, src_directory: str | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ftp_client = ftp_client
        self.src_directory = src_directory

    def describe(self) -> str:
        return "SFTP Delete Step"

    async def execute(self, i: Any) -> Any:
        if isinstance(i, FileConfigRawData):
            filename = os.path.join(i.file_config.inbound_directory, i.file_name)
        elif isinstance(i, RawData):
            if self.src_directory is None:
                raise RuntimeError("Attempted to delete a RawData object but src_directory was not set.")
            filename = os.path.join(self.src_directory, i.file_name)
        else:
            raise NotImplementedError(f"Unsupported input type: {type(i)}")
        try:
            self.ftp_client.delete_file(filename)
        except Exception as e:
            loguru.logger.warning(f"Failed to delete: {e}")
        return i
