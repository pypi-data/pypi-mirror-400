from typing import Protocol, Optional, Iterable, Dict, Any, runtime_checkable


class PriceMapperProtocol(Protocol):
    async def get_product_mappings(self, product_key: Optional[str]) -> Iterable:
        """Gets product mappings from integration"""

    async def get_location_mappings(self, location_key: Optional[str]) -> Iterable:
        """Gets location mappings from integration"""

    async def get_supplier_mappings(self, supplier_key: Optional[str]) -> Iterable:
        """Gets supplier mappings from integration"""


@runtime_checkable
class ExternalPriceMapperIntegration(Protocol):
    def get_mappings(self, query: Optional[str] = None, source_system: Optional[str] = None,
                     mapping_type: Optional[str] = None,
                     params: Optional[Dict[str, Any]] = None):
        """Gets mappings from integration"""
