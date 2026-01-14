from datetime import datetime, UTC

from pandas import DataFrame

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import FileReference, FileType


class DataFrameFlatFileExportStep(Step):
    def __init__(self, file_path: str, file_type: FileType, *args, **kwargs):
        super().__init__(*args, **kwargs)

        file_path = file_path
        if "{date}" in file_path:
            file_path = file_path.replace("{date}", datetime.now(UTC).strftime("%Y%m%d"))

        self.output = FileReference(file_path, file_type)

    def describe(self) -> str:
        return f"Exporting DataFrame to flat file {self.output.file_path}"

    async def execute(self, i: DataFrame) -> FileReference:
        if self.output.file_type == FileType.excel:
            i.to_excel(self.output.file_path, index=False)
        elif self.output.file_type == FileType.csv:
            i.to_csv(self.output.file_path, index=False)
        else:
            raise NotImplementedError(f"Unsupported file type: {self.output.file_type}")
        return self.output
