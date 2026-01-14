from datetime import datetime, timedelta
from typing import  List, override

import pytz
from bb_integrations_lib.models.rita.mapping import MappingType
from bb_integrations_lib.protocols.pipelines import Parser
from bb_integrations_lib.shared.model import PEPriceData
from loguru import logger


class AccessorialPricesParser(Parser):
    def __init__(self, tenant_name: str, source_system: str | None = None, timezone: str = "UTC"):
        self.tz = timezone
        super().__init__(tenant_name=tenant_name, source_system=source_system)

    def __repr__(self) -> str:
        return "Parse spot prices from rows to Sync Price Rows in Pricing Engine."

    @override
    async def parse(self, data: List[PEPriceData], mapping_type: MappingType | None = None) -> list[dict]:
        mapper = await self.load_mapper()
        mapping_failures = []
        translation_failures = []
        parsed_rows: List[dict] = []
        processed_assessorial_ids = set()
        latest_only = list(filter(lambda x: x.Rank == 1, data))
        for translated_row in latest_only:
            try:
                local_tz = pytz.timezone(self.tz)
                effective_from = datetime.now(local_tz).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) + timedelta(days=1)
                price_instrument_id = translated_row.PriceInstrumentId
                accessorial_id = mapper.get_gravitate_parent_id(str(price_instrument_id), MappingType.other)
                price = translated_row.CurvePointPrices[0].Value
                rate = mapper.get_gravitate_parent_id(str(accessorial_id), MappingType.other)
                row = {
                    "accessorial_id": accessorial_id,
                    "effective_from_date": effective_from.isoformat(),
                    "rate": str(AccessorialPricesParser.apply_rate(rate, price))
                }
                if accessorial_id not in processed_assessorial_ids:
                    parsed_rows.append(row)
                processed_assessorial_ids.add(accessorial_id)
            except KeyError as e:
                logger.warning(f"Failed to parse row {translated_row} due to mapping issue {e}")
                mapping_failures.append(translated_row)
                continue
            except Exception as e:
                logger.warning(f"Failed to parse row {translated_row} due to {e}")
                translation_failures.append(translated_row)
                continue
        return parsed_rows

    @staticmethod
    def apply_rate(rate, value) -> float:
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value: {value}")
        match rate.lower():
            case "positive":
                return float_value
            case "negative":
                return float_value * -1
            case _:
                raise NotImplementedError(f"Unsupported rate: {rate}")
