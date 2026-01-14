from datetime import datetime, UTC
from io import BytesIO
from typing import Tuple

import pandas as pd

from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import RawData


class DistributionReportDfToRawData(Step):
    def __init__(self, file_base_name: str, file_name_date_format: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_base_name = file_base_name
        self.file_name_date_format = file_name_date_format

    def describe(self) -> str:
        return "Distribution Report Dataframe to File"

    @property
    def file_name(self) -> str:
        return f"{self.file_base_name}_{datetime.now(UTC).strftime(self.file_name_date_format)}.xlsx"

    async def execute(self, data: Tuple[pd.DataFrame, pd.DataFrame]) -> RawData:
        buff = BytesIO()
        df_summary, df_detailed = data
        with pd.ExcelWriter(buff, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            df_detailed.to_excel(writer, sheet_name='Details', index=False)
        buff.seek(0)
        return RawData(data=buff.read(), file_name=self.file_name)


