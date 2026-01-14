from io import BytesIO
from loguru import logger

import pandas as pd

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.protocols.pipelines import Step, ParserBase, Input, Output
from bb_integrations_lib.shared.model import RawData
from pandas import DataFrame
from datetime import datetime, date, UTC


class BBDExportPayrollStep(Step):
    def __init__(self, sd_client: GravitateSDAPI, file_name: str, parser: type[ParserBase] | None = None,
                 parser_kwargs: dict | None = None, export_file: bool = True, target_date: str | None = None,
                 additional_ep_params: dict | None = None, *args, **kwargs):
        """
        Export a payroll file from S&D.

        :param export_file: If True, call the endpoint to export the file as an XLSX. If False, use the endpoint that
          provides JSON.
        """
        super().__init__(*args, **kwargs)
        self.sd_client = sd_client
        self.file_name = file_name
        self.export_file_only = export_file
        self.additional_endpoint_parameters = additional_ep_params or {
            "status": None,
            "driver_id": None,
            "updated_after": None,
        }
        if parser:
            self.custom_parser = parser
            self.custom_parser_kwargs = parser_kwargs or {}
        self.target_date = target_date

    def describe(self):
        return "Export Payroll from Supply and Dispatch"

    async def execute(self, last_sync_date: datetime | None = None) -> RawData:
        last_sync_date = self.last_sync_date(last_sync_date)
        dt = datetime.now(UTC)
        if self.export_file_only is True:
            logger.info(f"Exporting payroll file only for {last_sync_date}")
            df = await self.export_payroll_file_only(last_sync_date)
        else:
            logger.info(f"Exporting payroll json for {last_sync_date}")
            df =  await self.export_json(last_sync_date)
        return RawData(data=df.to_csv().encode("utf-8"), file_name=f"{self.file_name}_{dt.strftime("%Y%m%d%H%M%S")}")

    def last_sync_date(self, last_sync_date: datetime | None = None) -> str:
        if last_sync_date is None:
            if self.target_date is not None:
                last_sync_date = self.target_date
            elif self.pipeline_context.max_sync is not None:
                last_sync_date = self.pipeline_context.max_sync.max_sync_date.isoformat()
            else:
                last_sync_date = datetime.combine(date.today(), datetime.min.time()).isoformat()
        else:
            last_sync_date = last_sync_date.isoformat()
        return last_sync_date

    async def export_payroll_file_only(self, dt: datetime) -> DataFrame:
        resp = await self.sd_client.payroll_export_file(date=dt)
        df = pd.read_excel(BytesIO(resp.content),
                           dtype={"driver_source_id": str},
                           engine="openpyxl",
                           keep_default_na=False)
        if df.empty:
            raise Exception("No payroll data found")
        if hasattr(self, "custom_parser"):
            parser = self.custom_parser(tenant_name=self.tenant_name, **self.custom_parser_kwargs)
            df = await parser.parse(df)
            parser_logs = parser.get_logs()
            self.pipeline_context.included_files["parser_logs"] = parser_logs
        return df

    async def export_json(self, dt: datetime) -> DataFrame:
        resp = await self.sd_client.payroll_export(date=dt, **self.additional_endpoint_parameters)
        json_resp = resp.json()
        df = self.pre_parse_json(json_resp)
        if df.empty:
            raise Exception("No payroll data found")
        return df

    def pre_parse_json(self, json_resp: dict) -> DataFrame:
        all_rows = []
        for payroll_record in json_resp:
            header_info = {k: v for k, v in payroll_record.items() if k != 'detail'}
            details = payroll_record.get('detail', [])
            if not details:
                all_rows.append(header_info)
            else:
                for detail in details:
                    row = header_info.copy()
                    row.update(detail)
                    all_rows.append(row)
        df = pd.DataFrame(all_rows)
        datetime_columns = [
            'start_date', 'end_date', 'updated', 'shift_start',
            'shift_actual_start', 'shift_actual_end', 'overridden_datetime'
        ]
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df