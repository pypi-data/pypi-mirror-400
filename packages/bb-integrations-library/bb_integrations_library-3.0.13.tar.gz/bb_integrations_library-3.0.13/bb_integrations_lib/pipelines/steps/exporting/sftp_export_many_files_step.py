from typing import Any, Dict, List, Union

from bb_integrations_lib.models.pipeline_structs import BolExportResults
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import FileReference, RawData
from .sftp_export_file_step import SFTPExportFileStep


class SFTPExportManyFilesStep(Step):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(step_configuration)
        self.sftp_export_step = SFTPExportFileStep(step_configuration)

    def describe(self) -> str:
        return "SFTP Many Files Export"

    async def execute(self, files: List[Union[FileReference, RawData, BolExportResults]]) -> List[FileReference]:
        results = []
        for file in files:
            result = await self.sftp_export_step.execute(file)
            if result:
                results.append(result)
        return results