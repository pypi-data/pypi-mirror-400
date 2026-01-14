from zoneinfo import ZoneInfo

import dateutil
import json
from babel.numbers import parse_decimal, NumberFormatError
from dateutil.parser import parse
from dateutil.tz import gettz
from loguru import logger
from pandas import DataFrame
from typing import AsyncGenerator, Optional
from typing import override

from bb_integrations_lib.mappers.rita_mapper import RitaMapper, AsyncMappingProvider
from bb_integrations_lib.models.rita.issue import IssueCategory
from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.protocols.flat_file import TankSales
from bb_integrations_lib.protocols.pipelines import Parser
from bb_integrations_lib.shared.model import MappingMode

tzmapping = {
    'EST': gettz("US/Eastern"),
    'EDT': gettz("US/Eastern"),
    'CST': gettz("US/Central"),
    'CDT': gettz("US/Central"),
    'MST': gettz("US/Mountain"),
    'MDT': gettz("US/Mountain"),
    'PST': gettz("US/Pacific"),
    'PDT': gettz("US/Pacific"),
}


class SalesParser(Parser):
    def __init__(
            self,
            tenant_name: str,
            source_system: str | None = None,
            mapping_provider: Optional[AsyncMappingProvider] = None,
            included_payload: Optional[dict] = None,
            verbose: bool = False,
            deduplicate: bool = True,
    ):
        super().__init__(tenant_name, source_system, mapping_provider)
        self.verbose = verbose
        self.included_payload = included_payload or {}
        self.mapper: Optional[RitaMapper] = None
        self.deduplicate = deduplicate

    def dedupe_records(self, records: list[dict]) -> list[dict]:
        df = DataFrame(records)
        grouped_df = df.groupby(["site_id", "tank_id", "date"], as_index=False)["sales"].sum()
        grouped_df = grouped_df[["site_id", "tank_id", "date", "sales"]]
        return grouped_df.to_dict("records")

    @override
    async def parse(self, data: list[dict], mapping_type: MappingMode | None = None) -> AsyncGenerator[TankSales, None]:
        if mapping_type is None:
            logger.warning("TankSalesParser.parse mapping_type is None, defaulting to skip")
            mapping_type = MappingMode.skip
        self.mapper = await self.load_mapper()
        preparsed_records = self.preparse(data, mapping_type)
        if self.deduplicate:
            preparsed_records = self.dedupe_records(preparsed_records)

        for rec in preparsed_records:
            with logger.catch(message=f"Skipped record {rec} due to error"):
                ts = TankSales(
                    store_number=rec["site_id"],
                    tank_id=rec["tank_id"],
                    sales=float(rec["sales"]),
                    date=parse(rec['date']).replace(tzinfo=ZoneInfo("UTC")).isoformat(),
                )
            yield ts

    def preparse(self, records: list[dict], mapping_type: MappingMode) -> list:
        """Perform basic sanity checking on records and map tank and site ids, if applicable."""
        parsed_records = []
        mapping_failures = []
        for translated in records:
            try:
                translated_volume = translated.get("sales")
                if translated_volume == 'nan':
                    if self.verbose:
                        logger.warning(f"Skipped record {translated} due to NaN volume.")
                    continue
                try:
                    trans_vol_decimal = float(parse_decimal(translated_volume, locale="en_US"))
                    translated["sales"] = float(trans_vol_decimal)
                except NumberFormatError:
                    if self.verbose:
                        logger.warning(
                            f"Skipped record {translated} due to invalid volume value '{translated_volume}'.")
                    continue
                if trans_vol_decimal < 0:
                    if self.verbose:
                        logger.warning(f"Skipped record {translated} due to negative volume.")
                    continue
                if translated.get("tank_id") == "nan":
                    if self.verbose:
                        logger.warning(f"Skipped record {translated} due to NaN tank.")
                    continue
                if not translated.get("date"):
                    logger.warning(f"Skipped record {translated} due to missing date")
                    continue
                try:
                    date_parsed = dateutil.parser.parse(translated.get("date"), tzinfos=tzmapping)
                    translated["date"] = date_parsed.isoformat()
                except Exception as parse_error:
                    logger.warning(f"Skipped record {translated} due to date parsing error: {parse_error}")
                    continue

                if mapping_type == MappingMode.skip:
                    parsed_records.append(translated)
                elif mapping_type == MappingMode.partial or mapping_type == MappingMode.full:
                    try:
                        site_id = translated["site_id"]
                        tank_id = translated["tank_id"]
                        mapped_site_ids = self.mapper.get_gravitate_parent_ids(site_id, MappingType.site)
                        mapped_tank_ids = self.mapper.get_gravitate_child_ids(
                            site_id, tank_id.strip(), MappingType.tank
                        )
                        for site_id in mapped_site_ids:
                            for tank_id in mapped_tank_ids:
                                translated["site_id"] = site_id
                                translated["tank_id"] = tank_id
                                parsed_records.append(translated)
                    except (KeyError, ValueError) as e:
                        if mapping_type == MappingMode.partial:
                            parsed_records.append(translated)
                        else:
                            raise e

            except (KeyError, ValueError) as e:
                if self.verbose:
                    logger.warning(f"Skipped record {translated} due to error: {e}")
                mapping_failures.append(translated)
        if len(mapping_failures) > 0:
            self.record_issue(
                key_suffix="mapping_errors",
                name=f"Mapping errors",
                category=IssueCategory.TANK_READING,
                problem_short=f"{len(mapping_failures)} rows failed to map",
                problem_long=json.dumps(mapping_failures)
            )
        return parsed_records
