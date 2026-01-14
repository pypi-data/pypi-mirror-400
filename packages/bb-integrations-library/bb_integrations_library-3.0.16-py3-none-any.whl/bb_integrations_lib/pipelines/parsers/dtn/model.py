import math
from datetime import datetime, timedelta

from bb_integrations_lib.shared.model import ConfigMatchMode, ConfigMode, MappingMode
from pydantic import BaseModel, field_validator, Field
from dateutil.parser import parse
from bb_integrations_lib.shared.shared_enums import PriceType


class SupplyOwnerConfig(BaseModel):
    gravitate_id: str
    extend_by_days: int = 3
    expire_in_hours: int = 24

class DTNIntegrationConfig(BaseModel):
    config_name: str
    ftp_credentials: str
    file_match_mode: ConfigMatchMode = ConfigMatchMode.Partial
    config_match_mode: ConfigMode = ConfigMode.ByName
    mapping_mode: MappingMode = MappingMode.full
    supply_owners: list[SupplyOwnerConfig]

class DTNPriceRecord(BaseModel):
    supplier: str
    terminal: str
    product: str
    price: float
    source_system: str = "DTN"
    effective_from_date: datetime
    brand: str | None = None
    supply_owner: str | None = Field(default=None, alias="supply owner")
    price_type: PriceType | None = Field(default=PriceType.rack, alias="price type")
    contract: str | None = None
    model_config = {'extra': 'ignore', 'populate_by_name': True}

    @field_validator('supplier', 'terminal', 'product', 'price', mode='before')
    @classmethod
    def reject_nan(cls, v, info):
        if v is None:
            raise ValueError(f'{info.field_name} cannot be None')
        if isinstance(v, str) and v.lower() == 'nan':
            raise ValueError(f'{info.field_name} cannot be NaN')
        if isinstance(v, float) and math.isnan(v):
            raise ValueError(f'{info.field_name} cannot be NaN')
        return v

    @field_validator('effective_from_date', mode='before')
    @classmethod
    def parse_date(cls, v, info):
        if isinstance(v, str):
            try:
                return parse(v)
            except (ValueError, TypeError):
                raise ValueError(f'{info.field_name} must be a valid datetime string')
        return v

    @property
    def source_id(self) -> str:
        parts = [self.supplier, self.terminal, self.product, self.source_system, self.supply_owner]
        if self.brand:
            parts.append(self.brand)
        return "|".join(parts)

    @property
    def map_key(self):
        return {
            "supplier": self.supplier,
            "terminal": self.terminal,
            "product": self.product,
            "brand": self.brand,
        }

    def add_days(self, days: int) -> datetime:
        """Return effective_from_date plus the specified days."""
        return self.effective_from_date + timedelta(days=days)

    def add_hours(self, hours: int) -> datetime:
        """Return effective_from_date plus the specified hours."""
        return self.effective_from_date + timedelta(hours=hours)