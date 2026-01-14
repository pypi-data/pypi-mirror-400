from typing import Optional, Union, List, Dict
from collections.abc import Iterable
from loguru import logger

from bb_integrations_lib.gravitate.rita_api import RitaBackendAPI
from bb_integrations_lib.mappers.prices.model import PriceMappings, Group, PricingIntegrationConfig,\
    IntegrationMappingConfig
from bb_integrations_lib.mappers.prices.util import PricingIntegrationGetter, PricingIntegrationGetterProtocol
from bb_integrations_lib.models.rita.mapping import Map
from bb_integrations_lib.provider.sqlserver.client import SQLServerClient
from bb_integrations_lib.util.cache.custom_ttl_cache import CustomTTLCache
from bb_integrations_lib.util.cache.protocol import CustomTTLCacheProtocol


class PriceMapper:
    """Mapper instance to get all mapping data for needed for prices.
    Limited to:
        - Product, Location, Supplier and Publisher mappings
    """
    def __init__(
            self,
            config: PricingIntegrationConfig,
            ttl: int = 3600,
            debug_mode: bool = False,
            source_system: Optional[str] = None
    ):
        self.ttl = ttl
        self.config = config
        self.products_config: IntegrationMappingConfig = self.config.entity_config.get("products").mapping_integration
        self.locations_config: IntegrationMappingConfig = self.config.entity_config.get("locations").mapping_integration
        self.suppliers_config: IntegrationMappingConfig = self.config.entity_config.get("suppliers").mapping_integration
        self.publishers_config: IntegrationMappingConfig = self.config.entity_config.get("publishers").mapping_integration
        self.products_sql_query = self.products_config.query
        self.locations_sql_query = self.locations_config.query
        self.suppliers_sql_query = self.suppliers_config.query
        self.cache: CustomTTLCacheProtocol = CustomTTLCache(verbose=debug_mode)
        self.debug_mode = debug_mode
        self.source_system = source_system

        if debug_mode:
            logger.debug("DEBUG MODE ON")
        self.integration_getter: PricingIntegrationGetterProtocol = PricingIntegrationGetter(self.config)

    @property
    def ttl_cache(self):
        return self.cache

    async def _get_cached_data(self, cache_key: str, query_func) -> Iterable:
        """Generic method to retrieve cached data or fetch it using the provided query function"""

        @self.cache.ttl_cache(seconds=self.ttl, cache_key=cache_key)
        async def _get_data() -> Iterable:
            return await query_func() or {}
        return await _get_data()


    async def get_entity_mappings(self, key: str, mapping_type: Optional[str] = None, query: Optional[str] = None) -> Iterable:
        client = self.integration_getter.get_integration_mapping_client_by_entity(key)

        async def query_func():
            if isinstance(client, SQLServerClient):
                return client.get_mappings(query)
            elif isinstance(client, RitaBackendAPI):
                return await client.get_mappings(source_system=self.source_system,
                                           mapping_type=mapping_type)
            return {}
        return await self._get_cached_data(key, query_func)


    async def get_mappings(
            self,
            product_key: Optional[str] = "products",
            location_key: Optional[str] = "locations",
            supplier_key: Optional[str] = "suppliers",
            price_publisher_key: Optional[str] = "publishers"
    ) -> PriceMappings:
        return PriceMappings(
            product_mappings=await self.get_entity_mappings(product_key, mapping_type="product", query=self.products_sql_query),
            location_mappings=await self.get_entity_mappings(location_key, mapping_type="location", query=self.locations_sql_query),
            supplier_mappings=await self.get_entity_mappings(supplier_key, mapping_type="supplier", query=self.suppliers_sql_query),
            price_publishers=await self.get_entity_mappings(price_publisher_key, mapping_type="other")
        )

    @classmethod
    def group_rows(
            cls,
            rows: Union[List[Map], List[Dict]],
            external_id_field: str,
            gravitate_id_field: str,
            name_field: Optional[str] = None,
            is_rita: Optional[bool] = False,
    ) -> Dict[
        str, Group]:
        grouped = {}
        if is_rita:
            rows: List[Map]
            for row in rows:
                row_id = row.source_id
                children = [r.gravitate_id for r in row.children]
                if row_id not in grouped:
                    grouped[row_id] = Group(
                        name=row.gravitate_name,
                        ids=children,
                        length=len(children),
                        extra_data=row
                    )
            return grouped
        else:
            rows: List[Dict]
            for row in rows:
                row_id = row[external_id_field]
                row_guid = row[gravitate_id_field]
                row_name = row.get(name_field) if name_field else None
                if row_id not in grouped:
                    grouped[str(row_id)] = Group(
                        name=row_name,
                        ids=[row_guid],
                        length=1,
                        extra_data=row
                    )
                else:
                    group = grouped[row_id]
                    group.ids.append(row_guid)
                    group.length += 1
        return grouped


