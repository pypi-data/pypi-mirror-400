import copy
from typing import Dict, List, Tuple

from loguru import logger

from bb_integrations_lib.mappers.prices.model import Groups, \
    PricingIntegrationConfig
from bb_integrations_lib.mappers.prices.price_mapper import PriceMapper
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.exceptions import MappingNotFoundException
from bb_integrations_lib.shared.model import PEPriceData, SupplyPriceUpdateManyRequest


class PEParsePricesStep(Step):
    def __init__(self, config: PricingIntegrationConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        self.pm = PriceMapper(
            ttl=self.config.price_mapper_ttl,
            debug_mode=self.config.price_mapper_debug_mode,
            config=self.config
        )

    async def execute(self, rows: List[PEPriceData]) -> Tuple[
        List[SupplyPriceUpdateManyRequest], Dict]:
        return await self.process_rows(rows)

    def get_price_request(self, rows: List[PEPriceData]) -> List[SupplyPriceUpdateManyRequest]:

        res: List = []
        for row in rows:
            price = row.CurvePointPrices[0].Value
            res.append(
                SupplyPriceUpdateManyRequest
                    (
                    source_id=self.config.source_system_id,
                    source_system_id=self.config.source_system,
                    terminal_source_id=row.LocationSourceId if self.config.use_source_system_id else row.LocationSourceIdString,
                    terminal_source_system_id=row.LocationSourceId,
                    effective_from=row.EffectiveFromDateTime,
                    effective_to=row.EffectiveToDateTime,
                    expire=row.ExpirationDateTime,
                    price=price,
                    price_type="contract",
                    product_source_id=row.ProductSourceId if self.config.use_source_system_id else row.ProductSourceIdString,
                    product_source_system_id=row.ProductSourceId,
                    supplier_source_id=row.SupplierSourceId if self.config.use_source_system_id else row.SupplierSourceIdString,
                    supplier_source_system_id=row.SupplierSourceId,
                    timezone="America/Chicago",
                    curve_id=row.CurveId,
                    contract=row.SourceContractId
                )
            )
        return res

    def get_factor(self, **kwargs):
        result = 1
        for value in kwargs.values():
            result *= value
        return result

    async def process_rows(self, rows: List[PEPriceData]) -> Tuple[
        List[SupplyPriceUpdateManyRequest], Dict]:
        mappings = await self.get_mapping_groups()
        new_rows = self.get_price_request(rows)
        product_mappings = mappings.product_groups
        location_mappings = mappings.location_groups
        supplier_mappings = mappings.supplier_groups
        processed_rows = []
        error_dict = {}

        for idx, row in enumerate(new_rows):
            try:
                terminals = location_mappings.get(row.terminal_source_id)
                if terminals is None:
                    raise MappingNotFoundException(f"Missing terminal mapping for source_id: {row.terminal_source_id}")

                suppliers = supplier_mappings.get(row.supplier_source_id)
                if suppliers is None:
                    raise MappingNotFoundException(f"Missing supplier mapping for source_id: {row.supplier_source_id}")

                products = product_mappings.get(row.product_source_id)
                if products is None:
                    raise MappingNotFoundException(f"Missing product mapping for source_id: {row.product_source_id}")

                expected_combinations = self.get_factor(terminals_length=terminals.length,
                                                        suppliers_length=suppliers.length,
                                                        products_length=products.length)
                row_combinations = []
                for terminal_gravitate_id in terminals.ids:
                    for supplier_gravitate_id in suppliers.ids:
                        for product_gravitate_id in products.ids:
                            new_row = copy.deepcopy(row)
                            new_row.terminal_source_id = None
                            new_row.supplier_source_id = None
                            new_row.product_source_id = None
                            new_row.terminal_id = terminal_gravitate_id
                            new_row.supplier_id = supplier_gravitate_id
                            new_row.product_id = product_gravitate_id
                            row_combinations.append(new_row)
                assert len(
                    row_combinations) == expected_combinations, f"Expected {expected_combinations} combinations, got {len(row_combinations)}"
                processed_rows.extend(row_combinations)
            except MappingNotFoundException as mnfe:
                error_message = f"Mapping error: {str(mnfe)}"
                logger.error(f"Row {idx}: {error_message}")
                error_dict[idx] = {
                    "error_type": "MappingNotFoundException",
                    "message": str(mnfe),
                    "row_data": row.model_dump()
                }
                continue
            except AssertionError as ae:
                error_message = f"Combination count mismatch: {str(ae)}"
                logger.error(f"Row {idx}: {error_message}")
                error_dict[idx] = {
                    "error_type": "AssertionError",
                    "message": str(ae),
                    "row_data": row.model_dump(),
                    "expected_count": expected_combinations,
                    "actual_count": len(row_combinations)
                }
                continue
            except KeyError as ke:
                error_message = f"KeyError: {str(ke)}"
                logger.error(f"Row {idx}: {error_message}")
                error_dict[idx] = {
                    "error_type": "KeyError",
                    "message": str(ke),
                    "row_data": row.model_dump()
                }
                continue
            except Exception as e:
                error_message = f"Unexpected error: {str(e)}"
                logger.error(f"Row {idx}: {error_message}")
                error_dict[idx] = {
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "row_data": row.model_dump()
                }
                continue
        return processed_rows, error_dict

    async def get_mapping_groups(self) -> Groups:
        mappings = await self.pm.get_mappings()
        product_mappings = mappings.product_mappings
        location_mappings = mappings.location_mappings
        supplier_mappings = mappings.supplier_mappings
        terminal_groups = self.pm.group_rows(
            rows=location_mappings,
            external_id_field=self.config.location_external_keys.external_id_field,
            gravitate_id_field=self.config.location_external_keys.gravitate_id_field,
            name_field=self.config.location_external_keys.name_field,
        )
        product_groups = self.pm.group_rows(
            rows=product_mappings,
            external_id_field=self.config.product_external_keys.external_id_field,
            gravitate_id_field=self.config.product_external_keys.gravitate_id_field,
            name_field=self.config.product_external_keys.name_field,
        )
        supplier_groups = self.pm.group_rows(
            rows=supplier_mappings,
            external_id_field=self.config.supplier_external_keys.external_id_field,
            gravitate_id_field=self.config.supplier_external_keys.gravitate_id_field,
            name_field=self.config.supplier_external_keys.name_field,
        )
        return Groups(
            product_groups=product_groups,
            location_groups=terminal_groups,
            supplier_groups=supplier_groups,
        )

# TestPipeline deleted on May 20 2025. See previous commits for a copy.
