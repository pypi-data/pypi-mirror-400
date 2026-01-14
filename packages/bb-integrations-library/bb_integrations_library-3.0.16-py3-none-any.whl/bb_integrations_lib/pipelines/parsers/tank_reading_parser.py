import json
from typing import AsyncGenerator, Optional, cast
from typing import override

import dateutil
from babel.numbers import parse_decimal, NumberFormatError
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from dateutil.tz import gettz
from loguru import logger

from bb_integrations_lib.mappers.rita_mapper import RitaMapper, AsyncMappingProvider
from bb_integrations_lib.models.rita.issue import IssueCategory
from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.protocols.flat_file import TankReading, TankMonitorType
from bb_integrations_lib.protocols.pipelines import Parser
from bb_integrations_lib.shared.model import MappingMode
from bb_integrations_lib.util.utils import lookup

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


class TankReadingParser(Parser):
    def __init__(
            self,
            sd_client: GravitateSDAPI,
            source_system: str | None = None,
            mapping_provider: Optional[AsyncMappingProvider] = None,
            included_payload: Optional[dict] = None,
            verbose: bool = False,
            *args,
            **kwargs
    ):
        super().__init__(source_system, mapping_provider)
        self.sd_client = sd_client
        self.verbose = verbose
        self.included_payload = included_payload or {}
        self.mapper: Optional[RitaMapper] = None

    @override
    async def parse(self, data: list[dict], mapping_type: MappingMode | None = None) -> AsyncGenerator[
        TankReading, None]:
        if mapping_type is None:
            logger.warning("TankReadingParser.parse mapping_type is None, defaulting to skip")
            mapping_type = MappingMode.skip
        sd_store_lkp = await self.get_store_lkp()
        self.mapper = await self.load_mapper()
        preparsed_records = self.preparse(data, mapping_type)

        for rec in preparsed_records:
            with logger.catch(message=f"Skipped record {rec} due to error"):
                store_id = rec.get("site_id")
                sd_store = sd_store_lkp.get(store_id , {})
                store_tz = sd_store.get("timezone")
                yield TankReading(
                    store=store_id,
                    date=rec.get("reading_time"),
                    monitor_type=TankMonitorType.bbd,
                    timezone=rec.get("timezone") or store_tz,
                    volume=rec.get("volume"),
                    tank=rec.get("tank_id"),
                    payload=self.included_payload
                )
    async def get_store_lkp(self):
        stores = await self.sd_client.all_stores()
        return lookup(stores.json(), lambda x: x.get("store_number"))

    def preparse(self, records: list[dict], mapping_type: MappingMode) -> list:
        """Perform basic sanity checking on records and map tank and site ids, if applicable."""
        parsed_records = []
        mapping_failures = []
        for translated in records:
            try:
                translated_volume = translated.get("volume")
                if translated_volume == 'nan':
                    if self.verbose:
                        logger.warning(f"Skipped record {translated} due to NaN volume.")
                    continue
                try:
                    if isinstance(translated_volume, str):
                        trans_vol_decimal = float(parse_decimal(translated_volume, locale="en_US"))
                    else:
                        trans_vol_decimal = float(translated_volume)

                    translated["volume"] = trans_vol_decimal
                except NumberFormatError:
                    if self.verbose:
                        logger.warning(
                            f"Skipped record {translated} due to invalid volume value '{translated_volume}'.")
                    continue
                except TypeError:
                    if self.verbose:
                        logger.warning(
                            f"Skipped record {translated} due to invalid volume value '{translated_volume}'."
                        )
                    continue
                if trans_vol_decimal < 0:
                    if self.verbose:
                        logger.warning(f"Skipped record {translated} due to negative volume.")
                    continue
                if translated.get("tank_id") == "nan":
                    if self.verbose:
                        logger.warning(f"Skipped record {translated} due to NaN tank.")
                    continue
                if not translated.get("reading_time"):
                    logger.warning(f"Skipped record {translated} due to missing date")
                    continue
                try:
                    date_parsed = dateutil.parser.parse(translated.get("reading_time"), tzinfos=tzmapping)
                    translated["reading_time"] = date_parsed.isoformat()
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
                        mapped_tank_ids = self.mapper.get_gravitate_child_ids(site_id, tank_id.strip(), MappingType.tank)
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
