import json
from _datetime import datetime, timedelta
from typing import Dict, Any, List

from dateutil.parser import parse

from bb_integrations_lib.mappers.prices.model import PricingIntegrationConfig, EntityConfig, IntegrationMappingConfig
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.exceptions import MappingNotFoundException
from bb_integrations_lib.shared.model import PEPriceData, SupplyPriceUpdateManyRequest


class PEParsePricesToSDRequestStep(Step):
    def __init__(self, config: PricingIntegrationConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.pricing_strategy = self.config.strategy

    def describe(self) -> str:
        return f"Parse PE Prices -> SD Price Request"

    async def execute(self, rows: List[PEPriceData]) -> List[SupplyPriceUpdateManyRequest]:
        return await self.get_price_request(rows)

    def get_entity_config(self, key: str) -> EntityConfig:
        return self.config.entity_config.get(key)

    def filter_based_on_strategy(self, rows: List[PEPriceData]) -> List[PEPriceData]:
        filter_criteria = self.pricing_strategy.strategy_includes
        return list(filter(lambda r: r.Rank <= filter_criteria, rows))

    async def get_price_request(self, rows: List[PEPriceData]) -> List[SupplyPriceUpdateManyRequest]:
        res: List = []
        error_dict = {}
        product_entity: IntegrationMappingConfig = self.get_entity_config("products").external_system_integration
        location_entity: IntegrationMappingConfig = self.get_entity_config("locations").external_system_integration
        supplier_entity: IntegrationMappingConfig = self.get_entity_config("suppliers").external_system_integration
        product_key = product_entity.external_id_field
        location_key = location_entity.external_id_field
        supplier_key = supplier_entity.external_id_field
        rows = self.filter_based_on_strategy(rows)
        for idx, row in enumerate(rows):
            try:
                price = row.CurvePointPrices[0].Value
                row_dump = row.model_dump(mode='json')
                product_source_id = row_dump.get(product_key)
                effective_to = PEParsePricesToSDRequestStep.extend_effective_from(
                    effective_from=row.EffectiveFromDateTime,
                    effective_to=row.EffectiveToDateTime,
                    extend_by=row.ExtendByDays)
                if not product_source_id:
                    raise MappingNotFoundException(f"Product is missing source data")
                supplier_source_id = row_dump.get(supplier_key)
                if not supplier_source_id:
                    raise MappingNotFoundException(f"Supplier is missing source data")
                terminal_source_id = row_dump.get(location_key)
                if not terminal_source_id:
                    raise MappingNotFoundException(f"Location is missing source data")
                res.append(
                    SupplyPriceUpdateManyRequest
                        (
                        source_id=str(row.PriceInstrumentId), # TODO: document this change to use the price id
                        source_system_id=self.config.source_system,
                        terminal_source_id=terminal_source_id,
                        effective_from=row.EffectiveFromDateTime,
                        effective_to=effective_to,
                        price=price,
                        price_type=row.PriceType,
                        product_source_id=product_source_id,
                        supplier_source_id=supplier_source_id,
                        timezone=None, # New PE Fix
                        curve_id=row.CurvePointId,
                        contract=str(row_dump.get("SourceContractId")) if self.config.use_contract_id else None,
                        price_publisher=str(row.PricePublisherId),
                    )
                )
            except MappingNotFoundException as mnfe:
                error_dict[idx] = {
                    "error_type": "MappingNotFoundException",
                    "message": str(mnfe),
                    "row_data": row.model_dump()
                }
        log = {
            "parsed_rows": [row.model_dump(mode="json") for row in res],
            "errors": error_dict,
        }
        self.pipeline_context.included_files["parse pricing engine prices to SD schema step"] = json.dumps(log)
        return res

    @staticmethod
    def extend_effective_from(effective_from: str | datetime,
                              effective_to: str | datetime,
                              extend_by: int | None) -> str:
        if not extend_by:
            if isinstance(effective_to, datetime):
                return effective_to.isoformat()
            return effective_to
        if isinstance(effective_from, datetime):
            return (effective_from + timedelta(days=extend_by)).isoformat()
        elif isinstance(effective_from, str):
            dt = parse(effective_from)
            return (dt + timedelta(days=extend_by)).isoformat()

        else:
            raise ValueError(f'Unsupported type {type(effective_from)}')
