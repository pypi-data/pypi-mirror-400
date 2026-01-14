import os
from typing import Any, Dict

import pandas as pd

from bb_integrations_lib.models.pipeline_structs import BolExportResults, NoPipelineData
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.secrets.credential_models import FTPCredential
from bb_integrations_lib.shared.model import FileReference, File, RawData, FileConfigRawData


class SFTPExportFileStep(Step):
    def __init__(
            self,
            ftp_client: FTPIntegrationClient,
            ftp_destination_dir: str,
            field_sep: str = ",",
            allow_empty: bool = False,
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.ftp_client = ftp_client
        self.ftp_destination_dir = ftp_destination_dir
        self.field_sep = field_sep
        self.allow_empty = allow_empty

    def describe(self) -> str:
        return "SFTP File Export"

    async def execute(self, i: FileReference | RawData | BolExportResults | FileConfigRawData) -> FileReference:
        if isinstance(i, FileReference):
            if i.is_empty and not self.allow_empty:
                raise NoPipelineData("File is empty")
            file_name = os.path.basename(i.file_path)
            with open(i.file_path, "rb") as f:
                file_data = f.read()
            file = File(
                file_name=file_name, # The sftp_client adds another CSV to the file name, so strip it off here.
                file_data=file_data,
            )
            self.ftp_client.upload_file(file, self.ftp_destination_dir)
            return i
        elif isinstance(i, RawData) or isinstance(i, FileConfigRawData):
            if i.is_empty and not self.allow_empty:
                raise NoPipelineData("Data is empty")
            file = File(
                file_name = i.file_name,
                file_data = i.data
            )
            self.ftp_client.upload_file(file, self.ftp_destination_dir)
        elif isinstance(i, BolExportResults):
            if i.is_empty and not self.allow_empty:
                raise NoPipelineData("No contents to export")
            df = pd.DataFrame.from_records(i.orders)
            csv_text = df.to_csv(index=False, sep=self.field_sep)
            file = File(file_name=i.file_name, file_data=csv_text)
            self.ftp_client.upload_file(file, self.ftp_destination_dir)
        else:
            raise NotImplementedError(f"Cannot export unknown file wrapper type {type(i)} to SFTP")
