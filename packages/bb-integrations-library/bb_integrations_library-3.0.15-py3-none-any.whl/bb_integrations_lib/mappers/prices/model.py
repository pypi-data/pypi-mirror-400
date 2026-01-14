from enum import Enum
from typing import Optional, Dict, Union, List

from mergedeep import Strategy
from pydantic import BaseModel

from bb_integrations_lib.gravitate.model import System
from bb_integrations_lib.models.rita.mapping import Map


class Action(str, Enum):
    start = "start"
    stop = "stop"
    error = "error"


class IntegrationType(str, Enum):
    """Denotes available integration types for a Mapper"""
    sql = "sql"
    """Strictly limited to an MS SQL server database"""
    rita = "rita"
    """Strictly limited to rita mappings"""


class IntegrationMappingConfig(BaseModel):
    type: IntegrationType | System = None
    """The integration type to pull mappings from"""
    external_id_field: Optional[str] = None
    """External: to Gravitate. Denotes the id field to be used"""
    gravitate_id_field: Optional[str] = None
    """The Gravitate id field"""
    gravitate_name_field: Optional[str] = None
    external_name_field: Optional[str] = None
    query: Optional[str] = None
    """An optional query string"""


class EntityConfig(BaseModel):
    mapping_enabled: Optional[bool] = True
    mapping_integration: Optional[IntegrationMappingConfig] = {}
    external_system_integration: Optional[IntegrationMappingConfig] = {}

class PricePublisher(BaseModel):
    id: Optional[str] = None
    name: str
    price_type: str
    extend_by_days: Optional[int] = None

class PricingStrategy(str, Enum):
    use_latest = "Use Latest"
    """Only includes latest price -> may miss intraday changes"""
    use_prior_to_latest = "Use Prior to Latest"
    """Includes both the latest and latest minus one"""
    use_historic ="Use Historic"
    """Includes up to 10 historic changes for instrument since previous workday"""

    @property
    def strategy_includes(self) -> int:
        if self == PricingStrategy.use_latest:
            return 1
        if self == PricingStrategy.use_prior_to_latest:
            return 2
        if self == PricingStrategy.use_historic:
            return 10

class PricingIntegrationConfig(BaseModel):
    environment: str
    """The customer environment; i.e. TTE"""
    price_publishers: List[PricePublisher]
    """The list of price publisher from which to pull prices"""
    entity_config: Dict[str, EntityConfig] = {}
    """A key: EntityConfig pair, describing an entity config. i.e. {'products': EntityConfig}"""
    price_mapper_ttl: Optional[int] = 3600
    """The ttl cache release for the mapper"""
    price_mapper_debug_mode: Optional[bool] = False
    """Debug mode to enable verbose logging"""
    source_system: Optional[str] = None
    """The source system from where prices originate"""
    source_system_id: Optional[str] = None
    """The source system id from where prices originate"""
    use_contract_id: bool = True
    strategy: Optional[PricingStrategy] = PricingStrategy.use_historic



class Group(BaseModel):
    name: Optional[str] = None
    ids: list[str]
    length: int
    extra_data: Optional[Union[Dict, Map]] = None


class Groups(BaseModel):
    product_groups: Optional[Dict[str, Group]] = None
    location_groups: Optional[Dict[str, Group]] = None
    supplier_groups: Optional[Dict[str, Group]] = None
    price_publisher_groups: Optional[Dict[str, Group]] = None


class PriceMappings(BaseModel):
    product_mappings: Union[Dict, List]
    location_mappings: Union[Dict, List]
    supplier_mappings: Union[Dict, List]
    price_publishers: Union[Dict, List]


