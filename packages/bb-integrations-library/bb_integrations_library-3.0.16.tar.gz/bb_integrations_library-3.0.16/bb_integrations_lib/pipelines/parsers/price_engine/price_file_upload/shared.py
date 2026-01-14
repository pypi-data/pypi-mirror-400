from typing import List, Dict, Any

from dateutil.parser import parse

from bb_integrations_lib.protocols.pipelines import Parser
from bb_integrations_lib.shared.model import MappingMode


class PriceSyncParser(Parser):
    def __init__(self, tenant_name: str, source_system: str | None = None):
        super().__init__(tenant_name=tenant_name, source_system=source_system)

    def __repr__(self) -> str:
        return "Parse prices from rows to Sync Price Rows in Pricing Engine."

    async def parse(self, data: List[Dict], mapping_type: MappingMode | None = None) -> Any:
        pass

    @staticmethod
    def is_rvp(rvp: str) -> bool:
        try:
            return float(rvp) > 0.0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def format_rvp_product(product_key: str, rvp: str | None) -> str:
        if not rvp:
            return product_key
        rvp_str = str(rvp)
        if product_key.endswith(rvp_str):
            product_key = product_key[:-len(rvp_str)]
        product_key = product_key.rstrip('.')
        return f"{product_key}{float(rvp_str)}"

    @staticmethod
    def get_effective_to_date(effective_to_str: str | None,
                              effective_to_hrs_override: str | None,
                              effective_to_minutes_override: str | None) -> str | None:
        return PriceSyncParser.get_date_override(effective_to_str, effective_to_hrs_override,
                                                 effective_to_minutes_override)

    @staticmethod
    def get_effective_from_date(effective_from_str: str | None,
                                effective_from_hrs_override: str | None,
                                effective_from_minutes_override: str | None) -> str | None:
        return PriceSyncParser.get_date_override(effective_from_str, effective_from_hrs_override,
                                                 effective_from_minutes_override)

    @staticmethod
    def get_date_override(date_str: str | None,
                          date_to_hrs_override: str | None,
                          date_to_minutes_override: str | None) -> str | None:

        if not date_str:
            return date_str

        parsed_date = parse(date_str)

        if date_to_hrs_override and date_to_minutes_override:
            return parsed_date.replace(
                hour=int(date_to_hrs_override),
                minute=int(date_to_minutes_override),
                second=0
            ).isoformat()

        elif date_to_hrs_override:
            return parsed_date.replace(
                hour=int(date_to_hrs_override),
                minute=0,
                second=0
            ).isoformat()

        elif date_to_minutes_override:
            return parsed_date.replace(
                minute=int(date_to_minutes_override),
                second=0
            ).isoformat()

        else:
            return date_str
