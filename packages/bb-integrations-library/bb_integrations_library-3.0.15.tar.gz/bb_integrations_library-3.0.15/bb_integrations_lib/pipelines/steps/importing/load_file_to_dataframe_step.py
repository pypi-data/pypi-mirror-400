import asyncio
from typing import Dict

import pandas as pd

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import FileReference, FileType, RawData
from pandas import DataFrame


class LoadFileToDataFrameStep(Step):
    def __init__(self, sheet_name: str | int = 0, file_type: FileType | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sheet_name = sheet_name
        self.file_type = file_type

    def describe(self) -> str:
        return "Load file into dataframe"

    async def execute(self, i: FileReference | RawData) -> DataFrame:
        if isinstance(i, FileReference):
            if i.file_type == FileType.excel:
                if i.sheet_name is None:
                    return pd.read_excel(i.file_path, sheet_name=0)
                else:
                    return pd.read_excel(i.file_path, sheet_name=i.sheet_name)
            elif i.file_type == FileType.csv:
                return pd.read_csv(i.file_path)
            else:
                raise NotImplementedError()
        elif isinstance(i, RawData):
            if self.file_type is not None:
                if self.file_type == "csv":
                    return pd.read_csv(i.data)
            if i.file_name.endswith("csv"):
                return pd.read_csv(i.data)
            elif i.file_name.endswith("xlsx") or i.file_name.endswith("xls"):
                return pd.read_excel(i.data, sheet_name=0)

if __name__ == "__main__":
    async def main():
        input = FileReference("/home/ben-allen/Downloads/herdrich-payroll-test.xlsx", FileType.excel, "payroll")
        output = await LoadFileToDataFrameStep().execute(input)
        print(output.head(5))

    asyncio.run(main())