from typing import Callable

import pandas as pd
import polars as pl
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import RawData


class ExportDataFrameToRawDataStep(Step):
    def __init__(self, pandas_export_function: str, pandas_export_kwargs: dict,
                 file_name: str | Callable[[], str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pandas_export_function = pandas_export_function
        self.pandas_export_kwargs = pandas_export_kwargs
        self.file_name = file_name

    def _get_file_name(self) -> str:
        if callable(self.file_name):
            return self.file_name()
        else:
            return self.file_name

    def describe(self) -> str:
        return "Export a DataFrame to a file wrapped in a RawData object"

    async def execute(self, i: pd.DataFrame | pl.DataFrame) -> RawData:
        func = getattr(i, self.pandas_export_function)
        return RawData(data=func(**self.pandas_export_kwargs).encode("utf-8"), file_name=self._get_file_name())
