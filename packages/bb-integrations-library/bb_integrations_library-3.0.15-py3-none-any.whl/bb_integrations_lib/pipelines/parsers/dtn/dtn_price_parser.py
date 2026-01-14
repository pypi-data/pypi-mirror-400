from typing import AsyncGenerator, Optional
from typing import override

from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.pipelines.parsers.dtn.model import DTNIntegrationConfig, DTNPriceRecord
from bb_integrations_lib.shared.exceptions import MappingNotFoundException
from loguru import logger

from bb_integrations_lib.mappers.rita_mapper import RitaMapper, AsyncMappingProvider
from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.protocols.pipelines import Parser
from bb_integrations_lib.shared.model import MappingMode, SupplyPriceUpdateManyRequest
from bb_integrations_lib.util.utils import lookup
from pydantic import ValidationError


class DTNPriceParser(Parser):
    def __init__(
            self,
            source_system: str | None = None,
            mapping_provider: Optional[AsyncMappingProvider] = None,
            sd_client: GravitateSDAPI = None,
            price_config: DTNIntegrationConfig = None,
            **args
    ):
        super().__init__(source_system, mapping_provider)
        self.mapper: Optional[RitaMapper] = None
        self.sd_client = sd_client
        self.price_config = price_config
        self.supply_owner_configs_lkp_by_gravitate_id = lookup(self.price_config.supply_owners, lambda x: x.gravitate_id)

    @override
    async def parse(self, data: list[dict], mapping_type: MappingMode | None = None) -> AsyncGenerator[
        SupplyPriceUpdateManyRequest, None]:
        if mapping_type is None:
            logger.warning("DTNPriceParser.parse mapping_type is None, defaulting to skip")
            mapping_type = MappingMode.skip
        self.mapper = await self.load_mapper()
        preparsed_records = self.preparse(data, mapping_type)
        for rec in preparsed_records:
            with logger.catch(message=f"Skipped record {rec} due to error"):
                supply_owner_config = self.supply_owner_configs_lkp_by_gravitate_id.get(rec.supply_owner)
                extend_by_days = supply_owner_config.extend_by_days if supply_owner_config else 3
                expire_in_hours = supply_owner_config.expire_in_hours if supply_owner_config else 24
                yield SupplyPriceUpdateManyRequest(
                    source_id=rec.source_id,
                    source_system_id=rec.source_system,
                    terminal_id=rec.terminal,
                    product_id=rec.product,
                    supplier_id=rec.supplier,
                    effective_from=rec.effective_from_date,
                    effective_to=rec.add_days(extend_by_days),
                    price=rec.price,
                    price_type=rec.price_type,
                    timezone=None, # allways needs to be None
                    contract=rec.contract,
                    counterparty_id=rec.supply_owner,
                    expire=rec.add_hours(expire_in_hours),
                )

    async def get_store_lkp(self):
        stores = await self.sd_client.all_stores()
        return lookup(stores.json(), lambda x: x.get("store_number"))

    def try_to_map_composite_record(self, record: dict):
        try:
            ret = self.mapper.get_gravitate_id_by_composite(record, MappingType.composite)
            return ret
        except KeyError as e:
            raise MappingNotFoundException(f"Unable to find matching record for record {record}") from e

    def preparse(self, records: list[dict], mapping_type: MappingMode) -> list[DTNPriceRecord]:
        parsed_records = []
        mapping_failures = []
        validation_failures = []
        for translated in records:
            try:
                record = DTNPriceRecord(**translated)
                mapped_record = self.try_to_map_composite_record(record.map_key)
                mapped_record_key = {k.replace(" ", "_"): v for k, v in mapped_record.key.items()}
                updated_mapped_record = record.model_copy(update=mapped_record_key)
                parsed_records.append(updated_mapped_record)
            except ValidationError as e:
                validation_failures.append({
                    "record": translated,
                    "error": str(e),
                })
                logger.warning(f"Skipped invalid record {translated}: {e}")
                continue
            except MappingNotFoundException as mnfe:
                mapping_failures.append({
                    "record": translated,
                    "error": str(mnfe),
                })
                logger.warning(f"Skipped record due to mapping not found {translated}: {mnfe}")
                continue
        self.logs = {
            "validation_failures": validation_failures,
            "mapping_failures": mapping_failures,
            "successful_records": len(parsed_records),
        }
        return parsed_records
