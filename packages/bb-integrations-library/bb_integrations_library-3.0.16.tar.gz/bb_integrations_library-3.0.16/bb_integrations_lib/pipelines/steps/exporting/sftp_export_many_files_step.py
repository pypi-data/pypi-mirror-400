from typing import List, Union

from bb_integrations_lib.models.pipeline_structs import BolExportResults
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.shared.model import FileReference, RawData
from .sftp_export_file_step import SFTPExportFileStep


class SFTPExportManyFilesStep(Step):
    def __init__(
            self,
            ftp_client: FTPIntegrationClient,
            ftp_destination_dir: str,
            field_sep: str = ",",
            allow_empty: bool = False,
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.sftp_export_step = SFTPExportFileStep(
            ftp_client=ftp_client,
            ftp_destination_dir=ftp_destination_dir,
            field_sep=field_sep,
            allow_empty=allow_empty,
        )

    def describe(self) -> str:
        return "SFTP Many Files Export"

    async def execute(self, files: List[Union[FileReference, RawData, BolExportResults]]) -> List[FileReference]:
        results = []
        for file in files:
            result = await self.sftp_export_step.execute(file)
            if result:
                results.append(result)
        return results