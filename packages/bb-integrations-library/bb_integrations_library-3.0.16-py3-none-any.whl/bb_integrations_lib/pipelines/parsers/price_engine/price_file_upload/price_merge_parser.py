from typing import Dict, List, override, AsyncGenerator
from dateutil.parser import parse
from loguru import logger

from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.pipelines.parsers.price_engine.price_file_upload.shared import PriceSyncParser
from bb_integrations_lib.shared.model import MappingMode

from bb_integrations_lib.protocols.flat_file import PELookup, \
    PriceMergeIntegrationDTO, PriceMergeValue, PePriceMergeIntegration


class PricesMergeParser(PriceSyncParser):
    def __init__(self, tenant_name: str, source_system: str | None = None):
        super().__init__(tenant_name, source_system)

    def __repr__(self) -> str:
        return "Parse prices from rows to Merge Price Rows in Pricing Engine."

    @override
    async def parse(self, data: List[Dict], mapping_type: MappingMode | None = None) -> AsyncGenerator[
        PePriceMergeIntegration, None]:
        mapper = await self.load_mapper()
        mapping_failures = []
        translation_failures = []
        dtos: List[PriceMergeIntegrationDTO] = []
        for translated_row in data:
            try:
                row_is_rvp = PricesMergeParser.is_rvp(
                    translated_row.get('RVP', '0.0'))  # This will always be false if RVP does not exist
                price_publisher_name = translated_row['price_publisher']
                configuration = translated_row['configuration']
                supplier_key = translated_row['supplier_key']
                location_key = translated_row['location_key']
                product_key = translated_row['product_key']
                location_name = translated_row.get('location_name', None)
                product_name = translated_row.get('product_name', None)
                supplier_name = translated_row.get('supplier_name', None)
                price_factor = translated_row.get('price_factor')
                source_system_id = translated_row['source_system_id']
                effective_from_str = translated_row['date']
                effective_from_hrs_override = translated_row.get('effective_from_hrs_override', None)
                effective_from_mins_override = translated_row.get('effective_from_mins_override', None)
                effective_from = PricesMergeParser.get_effective_from_date(effective_from_str,
                                                                           effective_from_hrs_override,
                                                                           effective_from_mins_override)
                effective_to_str = translated_row.get('effective_to',
                                                      None)
                effective_to_hrs_override = translated_row.get('effective_to_hrs_override', None)
                effective_to_mins_override = translated_row.get('effective_to_mins_override', None)
                effective_to = PricesMergeParser.get_effective_to_date(effective_to_str,
                                                                       effective_to_hrs_override,
                                                                       effective_to_mins_override)
                price = translated_row['price']

                if row_is_rvp and not "RVP" in product_key:
                    product_key = PricesMergeParser.format_rvp_product(product_key, translated_row.get('RVP'))

                if price_factor is not None:
                    price = float(price) / int(price_factor)

                if mapping_type == MappingMode.full:
                    supplier_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                       source_child_id=supplier_key,
                                                                       mapping_type=MappingType.counterparty)
                    location_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                       source_child_id=location_key,
                                                                       mapping_type=MappingType.terminal
                                                                       )
                    product_source_id = mapper.get_gravitate_child_id(source_parent_id=configuration,
                                                                      source_child_id=product_key,
                                                                      mapping_type=MappingType.product)
                elif mapping_type == MappingMode.skip:
                    supplier_source_id = supplier_key
                    location_source_id = location_key
                    product_source_id = product_key
                else:
                    raise ValueError(f"Unsupported mapping type: {mapping_type}")
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
                    EffectiveFromDateTime=effective_from,
                    EffectiveToDateTime=effective_to,  # Effective to date is optional
                    PriceValues=[
                        PriceMergeValue(
                            Value=float(price),
                        )
                    ]
                ))
            except (KeyError, ValueError) as e:
                mapping_failures.append(translated_row)
                logger.warning(f"Skipped record {translated_row} due to Key Error or Value Error: {e}")
                continue
            except Exception as uh:
                translation_failures.append(translated_row)
                logger.warning(f"Skipped record {translated_row} due to unhandled exception: {uh.args}")
                continue
            if dtos and price_publisher_name and source_system_id:
                yield PePriceMergeIntegration(
                    IntegrationDtos=dtos,
                    SourceSystemId=int(source_system_id)
                )
            else:
                logger.warning("No valid records were processed to create an integration")
