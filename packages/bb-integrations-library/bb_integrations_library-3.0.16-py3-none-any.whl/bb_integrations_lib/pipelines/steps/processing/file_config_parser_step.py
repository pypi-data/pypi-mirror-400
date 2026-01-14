import json
import math
from enum import Enum
from typing import Dict, Iterable, List, Optional

import pandas as pd
import pytz
from dateutil.parser import parse
from loguru import logger
import traceback

from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.shared.model import RawData, FileConfigRawData, MappingMode
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.models.rita.config import FileConfig, ConfigAction
from bb_integrations_lib.models.rita.issue import IssueBase, IssueCategory
from bb_integrations_lib.protocols.flat_file import TankReading, TankMonitorType, PriceRow, DriverCredential, \
    BulkSyncIntegrationDTO, PriceInstrumentDTO, PELookup, PriceTypeDTO, PeBulkSyncIntegration, \
    PriceMergeIntegrationDTO, PriceMergeValue, PePriceMergeIntegration, TankSales
from bb_integrations_lib.mappers.rita_mapper import RitaMapper, RitaAPIMappingProvider
from babel.numbers import parse_decimal
from zipfile import BadZipFile
from dateutil.tz import gettz

import warnings

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


class FileConfigParserStep(
    Step[FileConfigRawData, Iterable[TankReading] | Iterable[PriceRow] | Iterable[
        DriverCredential] | Iterable[PeBulkSyncIntegration] | Iterable[PePriceMergeIntegration] | Iterable[
                                TankSales], None]):
    def __init__(self, step_configuration: Dict[str, str]):
        super().__init__(step_configuration)
        self.rita_url = step_configuration["rita_url"]
        self.rita_psk = None
        self.client_id = step_configuration["client_id"]
        self.client_secret = step_configuration["client_secret"]
        self.rita_tenant = step_configuration["rita_tenant"]
        self.output_type = step_configuration.get('output_type', "TankReading")
        self.verbose = step_configuration.get("verbose", False)
        self.mapping_type = step_configuration.get("mapping_type", MappingMode.full)
        self.included_payload = step_configuration.get("included_payload", {})

        warnings.warn(
            "FileConfigParserStep is deprecated. Use FileConfigParserV2 + a custom parser instead.",
            DeprecationWarning, stacklevel=2
        )

    def describe(self) -> str:
        return f"Parse Flat File into {self.output_type}"

    async def execute(self, i: FileConfigRawData) -> Iterable[TankReading] | Iterable[PriceRow] | Iterable[
        DriverCredential] | Iterable[PeBulkSyncIntegration] | Iterable[PePriceMergeIntegration | Iterable[TankSales]]:
        assert isinstance(i, FileConfigRawData)
        logger.info(f"Beginning data extract for file {i.file_name}")
        logger.debug(
            f"File Config: {i.file_config.client_name}, Inbound: {i.file_config.inbound_directory}, Archive: {i.file_config.archive_directory}")

        return list(await self.parse_raw_data(i))

    def parse_tank_and_site_ids(self, records: List[Dict], rd: FileConfigRawData, mapper: RitaMapper) -> Dict:
        """Only to be used by TankReading or TankSales"""
        translated_records = {}
        translation_failures = []
        mapping_failures = []
        for row in records:
            try:
                translated = self.translate_row(rd.file_config, row)
            except Exception as e:
                if self.verbose:
                    logger.warning(f"Translation failed for record {row}: {e}")
                translation_failures.append(row)
                continue
            try:
                if 'volume' in translated:
                    if translated['volume'] == 'nan':
                        if self.verbose:
                            logger.warning(f"Skipped record {row} due to NaN volume. Translated={translated}")
                        continue
                    if float(translated["volume"]) < 0:
                        if self.verbose:
                            logger.warning(f"Skipped record {row} due to Negative volume. Translated={translated}")
                        continue
                if 'tank_id' in translated:
                    if translated['tank_id'] == 'nan':
                        if self.verbose:
                            logger.warning(f"Skipped record {row} due to NaN tank. Translated={translated}")
                        continue
                if 'sales' in translated:
                    if translated['sales'] == 'nan':
                        if self.verbose:
                            logger.warning(f"Skipped record {row} due to NaN sales. Translated={translated}")
                        continue
                if self.mapping_type == MappingMode.skip:
                    key = f"{translated["site_id"]}_{translated["tank_id"]}"
                    translated_records[key] = translated
                elif self.mapping_type == MappingMode.partial or self.mapping_type == MappingMode.full:
                    try:
                        site_id = translated['site_id']
                        tank_id = translated["tank_id"]
                        mapped_site_ids = mapper.get_gravitate_parent_ids(site_id, MappingType.site)
                        mapped_tank_ids = mapper.get_gravitate_child_ids(site_id, tank_id.strip(), MappingType.tank)
                        for site_id in mapped_site_ids:
                            for tank_id in mapped_tank_ids:
                                key = f"{site_id}_{tank_id}"
                                translated["site_id"] = site_id
                                translated["tank_id"] = tank_id
                                translated_records[key] = {**translated}
                    except (KeyError, ValueError) as e:
                        if self.mapping_type == MappingMode.partial:
                            key = f"{translated["site_id"]}_{translated["tank_id"]}"
                            translated_records[key] = translated
                        else:
                            raise e
                else:
                    raise ValueError(f"MappingType {self.mapping_type} not supported")


            except (KeyError, ValueError) as e:
                if self.verbose:
                    logger.warning(f"Skipped record {row} due to error: {e}")
                mapping_failures.append(translated)
        self.handle_issues(translation_failures, mapping_failures, rd, output_type=self.output_type)
        return translated_records

    def parse_price_row(self, records: List[Dict], rd: FileConfigRawData, mapper: Optional[RitaMapper] = None) -> \
            Iterable[PriceRow]:
        translation_failures = []
        mapping_failures = []
        for row in records:
            try:
                translated = self.translate_row(rd.file_config, row)
                yield PriceRow(
                    effective_from=translated["effective_from"],
                    effective_to=translated["effective_to"],
                    price=float(translated["price"]),
                    price_type=translated["price_type"],
                    contract=translated.get("contract", None),
                    timezone=translated.get("timezone", None),
                    terminal_id=translated.get("terminal_id", None),
                    terminal_source_id=translated.get("terminal_source_id", None),
                    terminal_source_system_id=translated.get("terminal_source_system_id", None),
                    terminal=translated.get("terminal", None),
                    product_id=translated.get("product_id", None),
                    product_source_id=translated.get("product_source_id", None),
                    product_source_system_id=translated.get("product_source_system_id", None),
                    product=translated.get("product", None),
                    supplier_id=translated.get("supplier_id", None),
                    supplier_source_id=translated.get("supplier_source_id", None),
                    supplier_source_system_id=translated.get("supplier_source_system_id", None),
                    counterparty_source_id=translated.get("counterparty_source_id", None),
                    counterparty_source_system_id=translated.get("counterparty_source_system_id", None),
                    supplier=translated.get("supplier", None),
                    enabled=bool(translated.get("enabled", None)),
                    disabled_until=translated.get("disabled_until", None),
                    expire=translated.get("expire", None),
                    min_quantity=translated.get("min_quantity", None),
                    max_quantity=translated.get("max_quantity", None),
                    curve_id=translated.get("curve_id", None),
                    row=translated.get("row", None),
                )
            except(KeyError, ValueError) as e:
                translation_failures.append(row)
                if self.verbose:
                    logger.warning(f"Skipped record {row} due to error: {e}")
        self.handle_issues(translation_failures, mapping_failures, rd, output_type=self.output_type)

    def parse_tank_reading_rows(self, records: List[Dict], rd: FileConfigRawData,
                                mapper: Optional[RitaMapper] = None) -> Iterable[TankReading]:
        translated_records = self.parse_tank_and_site_ids(records, rd, mapper)

        for translated_record in translated_records.values():
            if translated_record.get("reading_time") is None:
                logger.warning(f"Skipped record {translated_record} due missing date")
                continue
            try:
                date_parsed = parse(translated_record.get("reading_time"), tzinfos=tzmapping).isoformat()
            except Exception as parse_error:
                logger.warning(f"Skipped record {translated_record} due to date parsing error: {parse_error}")
                continue
            try:
                yield TankReading(
                    store=translated_record.get("site_id"),
                    date=date_parsed,
                    monitor_type=TankMonitorType.bbd,
                    timezone=translated_record.get("timezone"),
                    volume=translated_record.get("volume"),
                    tank=translated_record.get("tank_id"),
                    payload=self.included_payload

                )
            except ValueError as e:
                # ValueError here probably means a volume has a , in the number or is a string. Parse
                # it with Babel instead.
                yield TankReading(
                    store=translated_record.get("site_id"),
                    date=date_parsed,
                    monitor_type=TankMonitorType.bbd,
                    timezone=translated_record.get("timezone"),
                    volume=float(parse_decimal(translated_record.get("volume"), locale="en_US")),
                    tank=translated_record.get("tank_id"),
                    payload=self.included_payload
                )
            except Exception as ee:
                logger.warning(f"Skipped record {translated_record} due to error: {ee}")
                continue

    def parse_tank_sales_rows(self, records: List[Dict], rd: FileConfigRawData, mapper: Optional[RitaMapper] = None) -> \
            Iterable[TankSales]:
        translated_records = self.parse_tank_and_site_ids(records, rd, mapper)
        ll = []
        errors = []
        for key in translated_records:
            site_id = translated_records[key].get("site_id", "")
            tank_id = translated_records[key].get("tank_id", "")
            try:
                tz = translated_records.get(key, {}).get("timezone")
                ll.append(TankSales(
                    store_number=site_id,
                    tank_id=tank_id,
                    sales=float(translated_records.get(key)['sales']),
                    date=parse(translated_records.get(key)['date'], tzinfos=tzmapping).replace(
                        tzinfo=(pytz.timezone(tz)), hour=0, minute=0, second=0, microsecond=0).isoformat(),
                ))
            except ValueError as e:
                errors.append({
                    "error": f"ValueError: {str(e)}",
                    "row": f"record containing site: {site_id} and tank: {tank_id}",
                })
                if self.verbose:
                    logger.warning(
                        f"Skipped containing site: {site_id} and tank: {tank_id} due to error: {str(e)}")
                continue
            except KeyError as ke:
                errors.append({
                    "error": f"KeyError: {str(ke)}",
                    "row": f"record containing site: {site_id} and tank: {tank_id}",
                })
                if self.verbose:
                    logger.warning(
                        f"Skipped record containing site: {site_id} and tank: {tank_id} due to error: {str(ke)}")
                continue
            except TypeError as tpe:
                errors.append({
                    "error": f"TypeError: {str(tpe)}",
                    "row": f"record containing site: {site_id} and tank: {tank_id}",
                })
                if self.verbose:
                    logger.warning(
                        f"Skipped record containing site: {site_id} and tank: {tank_id} due to error: {str(tpe)}")
                continue
            except Exception as ee:
                errors.append({
                    "error": f"Unknown error: {str(ee)}",
                    "row": f"record containing site: {site_id} and tank: {tank_id}",
                })
                if self.verbose:
                    logger.warning(
                        f"Skipped record containing site: {site_id} and tank: {tank_id} due to error: {str(ee)}")
                continue
        return ll

    def parse_credential_rows(self, records: List[Dict], rd: FileConfigRawData, mapper: Optional[RitaMapper] = None) -> \
            Iterable[DriverCredential]:
        translation_failures = []
        mapping_failures = []
        for row in records:
            try:
                translated = self.translate_row(rd.file_config, row)
                credential_ids = mapper.get_gravitate_parent_ids(source_id=translated['credential_id'],
                                                                 mapping_type=MappingType.credential)
                driver_ids = mapper.get_gravitate_parent_ids(source_id=translated['driver_id'],
                                                             mapping_type=MappingType.driver)
                expiration_date = translated.get('expiration_date')
                if expiration_date in ['nan']:
                    if self.verbose:
                        logger.warning(f"Skipped record due to NaN expiration date")
                    continue
                for credential_id in credential_ids:
                    for driver_id in driver_ids:
                        yield DriverCredential(
                            driver_id=driver_id,
                            credential_id=credential_id,
                            certification_date=translated.get('certification_date'),
                            expiration_date=expiration_date
                        )
            except (KeyError, ValueError) as e:
                translation_failures.append(row)
                if self.verbose:
                    logger.warning(f"Skipped record {row} due to error: {e}")
                continue
            self.handle_issues(translation_failures, mapping_failures, rd, output_type=self.output_type)

    def parse_price_sync_rows(self, records: List[Dict], rd: FileConfigRawData, mapper: Optional[RitaMapper] = None) -> \
            Iterable[PeBulkSyncIntegration]:
        translation_failures = []
        mapping_failures = []
        dtos: List[PriceInstrumentDTO] = []
        price_publisher_name = None
        posting_type = "Posting"
        source_system_id = None
        for row in records:
            try:
                row_is_rvp = FileConfigParserStep.is_rvp(row.get('RVP', '0.0'))
                translated = self.translate_row(rd.file_config, row)
                price_publisher_name = translated['price_publisher']
                configuration = translated['configuration']
                supplier_key = translated['supplier_key']
                location_key = translated['location_key']
                product_key = translated['product_key']
                posting_type = translated.get('posting_type', "Posting")
                location_name = translated.get('location_name', None)
                product_name = translated.get('product_name', None)
                supplier_name = translated.get('supplier_name', None)
                if row_is_rvp and not "RVP" in product_key:
                    product_key = FileConfigParserStep.format_rvp_product(product_key, row['RVP'])
                if '.' in product_key and not row_is_rvp:
                    product_key = product_key.split('.')[0]
                source_system_id = translated['source_system_id']

                if self.mapping_type == MappingMode.full:
                    supplier_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                       source_child_id=supplier_key,
                                                                       mapping_type=MappingType.counterparty)
                    location_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                       source_child_id=location_key,
                                                                       mapping_type=MappingType.terminal)
                    product_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                      source_child_id=product_key,
                                                                      mapping_type=MappingType.product)
                elif self.mapping_type == MappingMode.skip:
                    supplier_source_id = supplier_key
                    location_source_id = location_key
                    product_source_id = product_key
                else:
                    raise ValueError(f"Unsupported mapping type: {self.mapping_type}")
                if product_name is not None and location_name is not None and supplier_name is not None:
                    price_instrument_name = f"{product_name} @ {location_name} - {supplier_name}"
                else:
                    price_instrument_name = f"{product_source_id} @ {location_source_id} - {supplier_source_id}"
                price_instrument_source_string_id = f"{price_publisher_name} - {price_instrument_name}"
                dtos.append(PriceInstrumentDTO(
                    Name=price_instrument_name,
                    Abbreviation=price_instrument_name,
                    SourceIdString=price_instrument_source_string_id,
                    ProductLookup=PELookup(
                        SourceIdString=product_source_id,
                        SourceSystemId=int(source_system_id)
                    ),
                    LocationLookup=PELookup(
                        SourceIdString=location_source_id,
                        SourceSystemId=int(source_system_id)
                    ),
                    CounterPartyLookup=PELookup(
                        SourceIdString=supplier_source_id,
                        SourceSystemId=int(source_system_id)
                    )
                ))
            except (KeyError, ValueError) as e:
                mapping_failures.append(row)
                logger.warning(f"Skipped record {row} due to Key Error or Value Error: {e}")

                continue
            except Exception as uh:
                translation_failures.append(row)
                if self.verbose:
                    logger.warning(f"Skipped record {row} due to unhandled exception: {uh.args}")
                if irc := self.pipeline_context.issue_report_config:
                    if len(translation_failures) > 0:
                        key = f"{irc.key_base}_{rd.file_config.config_id}_translation_error"
                        self.pipeline_context.issues.append(IssueBase(
                            key=key,
                            config_id=rd.file_config.config_id,
                            name=f"Translation error - {rd.file_config.client_name}",
                            category=IssueCategory.TANK_READING,
                            problem_short=f"{rd.file_name}: At least 1 row failed to translate",
                            problem_long=json.dumps(translation_failures)
                        ))
                continue

        if dtos and price_publisher_name and source_system_id:
            try:
                yield PeBulkSyncIntegration(
                    IntegrationDtos=[
                        BulkSyncIntegrationDTO(
                            Name=price_publisher_name,
                            Abbreviation=price_publisher_name,
                            SourceIdString=price_publisher_name,
                            PriceInstrumentDTOs=dtos,
                            PriceTypeDTOs=[
                                PriceTypeDTO(
                                    PriceTypeMeaning=posting_type
                                )
                            ]
                        )
                    ],
                    SourceSystemId=int(source_system_id)
                )

            except Exception as ex:
                logger.warning(f"Unexpected error when yielding integration: {ex}")
                if irc := self.pipeline_context.issue_report_config:
                    key = f"{irc.key_base}_{rd.file_config.config_id}_parser_error"
                    self.pipeline_context.issues.append(IssueBase(
                        key=key,
                        config_id=rd.file_config.config_id,
                        name=f"Parser error - {rd.file_config.client_name}",
                        category=IssueCategory.REFERENCE_DATA,
                        problem_short=f"{rd.file_name}: Unexpected exception",
                        problem_long=json.dumps({
                            "exception_type": type(ex).__name__,
                            "args": list(ex.args) if ex.args else []
                        })
                    ))
        else:
            logger.warning("No valid records were processed to create an integration")

    def parse_price_merge_rows(self, records: List[Dict], rd: FileConfigRawData, mapper: Optional[RitaMapper] = None) -> \
            Iterable[PePriceMergeIntegration]:
        translation_failures = []
        mapping_failures = []
        dtos: List[PriceMergeIntegrationDTO] = []
        price_publisher_name = None
        posting_type = "Posting"  # Default value
        source_system_id = None
        for row in records:
            try:
                row_is_rvp = FileConfigParserStep.is_rvp(row.get('RVP', '0.0'))
                translated = self.translate_row(rd.file_config, row)
                price_publisher_name = translated['price_publisher']
                configuration = translated['configuration']
                supplier_key = translated['supplier_key']
                location_key = translated['location_key']
                product_key = translated['product_key']
                location_name = translated.get('location_name', None)
                product_name = translated.get('product_name', None)
                supplier_name = translated.get('supplier_name', None)
                price_factor = translated.get('price_factor')
                if row_is_rvp and not "RVP" in product_key:
                    product_key = FileConfigParserStep.format_rvp_product(product_key, row['RVP'])
                if '.' in product_key and not row_is_rvp:
                    product_key = product_key.split('.')[0]
                source_system_id = translated['source_system_id']
                posting_type = translated.get('posting_type', "Posting")
                date_str = translated['date']
                price = translated['price']
                if price_factor is not None:
                    price = float(price) / int(price_factor)

                if self.mapping_type == MappingMode.full:
                    supplier_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                       source_child_id=supplier_key,
                                                                       mapping_type=MappingType.counterparty)
                    location_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                       source_child_id=location_key,
                                                                       mapping_type=MappingType.terminal)
                    product_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                      source_child_id=product_key,
                                                                      mapping_type=MappingType.product)
                elif self.mapping_type == MappingMode.skip:
                    supplier_source_id = supplier_key
                    location_source_id = location_key
                    product_source_id = product_key
                else:
                    raise ValueError(f"Unsupported mapping type: {self.mapping_type}")
                if product_name is not None and location_name is not None and supplier_name is not None:
                    price_instrument_name = f"{product_name} @ {location_name} - {supplier_name}"
                else:
                    price_instrument_name = f"{product_source_id} @ {location_source_id} - {supplier_source_id}"
                price_instrument_source_string_id = f"{price_publisher_name} - {price_instrument_name}"
                dtos.append(PriceMergeIntegrationDTO(
                    PriceInstrumentLookup=PELookup(
                        SourceIdString=price_instrument_source_string_id,
                        SourceSystemId=int(source_system_id)
                    ),
                    EffectiveFromDateTime=parse(date_str).isoformat(),
                    PriceValues=[
                        PriceMergeValue(
                            Value=float(price),
                        )
                    ]
                ))


            except (KeyError, ValueError) as e:
                mapping_failures.append(row)
                logger.warning(f"Skipped record {row} due to Key Error or Value Error: {e}")
                continue
            except Exception as uh:
                translation_failures.append(row)
                if self.verbose:
                    logger.warning(f"Skipped record {row} due to unhandled exception: {uh.args}")
                if irc := self.pipeline_context.issue_report_config:
                    if len(translation_failures) > 0:
                        key = f"{irc.key_base}_{rd.file_config.config_id}_translation_error"
                        self.pipeline_context.issues.append(IssueBase(
                            key=key,
                            config_id=rd.file_config.config_id,
                            name=f"Translation error - {rd.file_config.client_name}",
                            category=IssueCategory.TANK_READING,
                            problem_short=f"{rd.file_name}: At least 1 row failed to translate",
                            problem_long=json.dumps(translation_failures)
                        ))
                continue
        if dtos and price_publisher_name and source_system_id:
            try:
                yield PePriceMergeIntegration(
                    IntegrationDtos=dtos,
                    SourceSystemId=int(source_system_id)
                )
            except Exception as ex:
                logger.warning(f"Unexpected error when yielding integration: {ex}")
                if irc := self.pipeline_context.issue_report_config:
                    key = f"{irc.key_base}_{rd.file_config.config_id}_parser_error"
                    self.pipeline_context.issues.append(IssueBase(
                        key=key,
                        config_id=rd.file_config.config_id,
                        name=f"Parser error - {rd.file_config.client_name}",
                        category=IssueCategory.PRICE,
                        problem_short=f"{rd.file_name}: Unexpected exception",
                        problem_long=json.dumps({
                            "exception_type": type(ex).__name__,
                            "args": list(ex.args) if ex.args else []
                        })
                    ))

    def handle_issues(self, translation_failures: List, mapping_failures: List, rd: FileConfigRawData,
                      output_type: Optional[str] = None):
        if not output_type or output_type is None:
            output_type = self.output_type
        if irc := self.pipeline_context.issue_report_config:
            if output_type == "TankReading":
                if len(translation_failures) > 0:
                    key = f"{irc.key_base}_{rd.file_config.config_id}_translation_error"
                    self.pipeline_context.issues.append(IssueBase(
                        key=key,
                        config_id=rd.file_config.config_id,
                        name=f"Translation error - {rd.file_config.client_name}",
                        category=IssueCategory.TANK_READING,
                        problem_short=f"{rd.file_name}: At least 1 row failed to translate",
                        problem_long=json.dumps(translation_failures)
                    ))

                if len(mapping_failures) > 0:
                    key = f"{irc.key_base}_{rd.file_config.config_id}_mapping_error"
                    self.pipeline_context.issues.append(IssueBase(
                        key=key,
                        config_id=rd.file_config.config_id,
                        name=f"Mapping error - {rd.file_config.client_name}",
                        category=IssueCategory.TANK_READING,
                        problem_short=f"{rd.file_config.client_name}: At least 1 row failed to map",
                        problem_long=json.dumps(mapping_failures)
                    ))

    async def parse_raw_data(self, rd: FileConfigRawData) -> Iterable[
        TankReading | PriceRow | DriverCredential | PeBulkSyncIntegration | PePriceMergeIntegration | TankSales]:
        try:
            records, raw_data, mapper = await self.get_records(rd)
            if self.output_type == "TankReading":
                return self.parse_tank_reading_rows(records, rd, mapper)
            if self.output_type == "TankSales":
                return self.parse_tank_sales_rows(records, rd, mapper)
            elif self.output_type == "PriceRow":
                return self.parse_price_row(records, rd, mapper)
            elif self.output_type == "Credential":
                return self.parse_credential_rows(records, rd, mapper)
            elif self.output_type == "PeStructureSync":
                return self.parse_price_sync_rows(records, rd, mapper)
            elif self.output_type == "PePriceMerge":
                return self.parse_price_merge_rows(records, rd, mapper)
            else:
                raise ValueError(
                    f"Invalid output_type: '{self.output_type}'. Only 'TankReading', 'PriceRow', 'Credential', 'PeStructureSync','PePriceMerge' or 'TankSales' are supported.")
        except Exception as e:
            logger.error(f"Error in parse_raw_data: {e}")
            if irc := self.pipeline_context.issue_report_config:
                key = f"{irc.key_base}_{rd.file_config.config_id}_parser_error"
                self.pipeline_context.issues.append(IssueBase(
                    key=key,
                    config_id=rd.file_config.config_id,
                    name=f"Parser error - {rd.file_config.client_name}",
                    category=IssueCategory.UNKNOWN,
                    problem_short=f"{rd.file_name}: Unexpected exception in parse_raw_data",
                    problem_long=json.dumps({
                        "exception_type": type(e).__name__,
                        "args": list(e.args) if e.args else []
                    })
                ))
            raise

    async def get_records(self, rd: RawData):  # Misstyped
        assert isinstance(rd, FileConfigRawData)
        try:
            if hasattr(rd.data, 'seek'):
                rd.data.seek(0)
            match rd.file_config.file_extension:
                case "csv1":
                    """This format will skip the top row of the file"""
                    temp_df = pd.read_csv(rd.data, index_col=False, dtype=str, skiprows=1)
                    temp_df = temp_df.rename(columns=lambda x: x.strip())
                    records = temp_df.to_dict(orient='records')
                case "csv":
                    temp_df = pd.read_csv(rd.data, index_col=False, dtype=str)
                    temp_df = temp_df.rename(columns=lambda x: x.strip())
                    records = temp_df.to_dict(orient="records")
                case "csv_headless":
                    """This format will treat the file as headless and load in generic column names 'col 1', 'col 2', etc."""
                    df = pd.read_csv(rd.data, index_col=False, dtype=str, header=None)
                    df.columns = [f"col {i + 1}" for i in range(df.shape[1])]
                    records = df.to_dict(orient='records')
                case "xls" | "xlsx":
                    """
                    Reads an excel and returns a dataframe
                    """
                    try:
                        temp_df = pd.read_excel(rd.data, engine="openpyxl", dtype=str)
                        temp_df = temp_df.rename(columns=lambda x: x.strip())
                        records = temp_df.to_dict(orient='records')
                    except (OSError, BadZipFile) as e:
                        # The file may be an old binary Excel file.
                        records = pd.read_excel(rd.data, engine="xlrd", dtype=str).to_dict(orient='records')
                case "html":
                    """
                    Reads an html and returns a dataframe
                    """
                    data = pd.read_html(rd.data, header=0)
                    merged = pd.concat(data)
                    records = merged.to_dict(orient="records")
                case _:
                    raise ValueError("The file_extension in the file config is not supported")

            rd.data_buffer_bkp = pd.DataFrame(records).to_csv(index=False)
            mapper = RitaMapper(
                provider=RitaAPIMappingProvider(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    rita_tenant=self.rita_tenant,
                ),
                source_system=rd.file_config.source_system,
            )
            await mapper.load_mappings_async()

            return records, rd, mapper
        except Exception as e:
            if irc := self.pipeline_context.issue_report_config:
                key = f"{irc.key_base}_{rd.file_config.config_id}_failed_to_load"
                name = f"Failed to load file \"{rd.file_name}\" for client {rd.file_config.client_name}"
                self.pipeline_context.issues.append(IssueBase(
                    key=key,
                    config_id=rd.file_config.config_id,
                    name=name,
                    category=IssueCategory.TANK_READING,
                    problem_short=str(e),
                    problem_long=traceback.format_exc()
                ))
            raise e

    def translate_row(self, file_config: FileConfig, row: dict) -> Dict:
        output_row = {}
        for column in file_config.cols:
            if len(column.file_columns) == 0:
                output_row[column.column_name] = None
            elif column.action == ConfigAction.concat:
                concatenated = ""
                for entry in column.file_columns:
                    stripped_entry = entry.strip()
                    if stripped_entry in row:
                        value = row[stripped_entry]
                        if value is None or (isinstance(value, float) and math.isnan(value) or pd.isna(value)):
                            concatenated += ""
                        else:
                            concatenated += str(value)
                    else:
                        concatenated += str(entry)
                output_row[column.column_name] = concatenated
            elif column.action == ConfigAction.parse_date:
                output_row[column.column_name] = str(pd.to_datetime(row[column.file_columns[0]]))
            elif column.action == ConfigAction.add:
                output_row[column.column_name] = column.file_columns[0]
            elif column.action == ConfigAction.remove_leading_zeros:
                output_row[column.column_name] = self.strip_leading_zeroes(str(row[column.file_columns[0]]))
            elif column.action == ConfigAction.remove_trailing_zeros:
                output_row[column.column_name] = self.strip_trailing_zeroes(str(row[column.file_columns[0]]))
            else:
                output_row[column.column_name] = str(row[column.file_columns[0]])
        return output_row

    @staticmethod
    def strip_leading_zeroes(row: str):
        return row.lstrip('0')

    @staticmethod
    def strip_trailing_zeroes(row: str):
        return row.rstrip('0')

    @staticmethod
    def is_rvp(rvp: str) -> bool:
        try:
            return float(rvp) > 0.0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def format_rvp_product(product_key: str, rvp: str) -> str:
        rvp_str = str(rvp)
        if product_key.endswith(rvp_str):
            product_key = product_key[:-len(rvp_str)]
        product_key = product_key.rstrip('.')
        return f"{product_key}{float(rvp_str)}"
