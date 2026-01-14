from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Dict, Self
import json
import pandas as pd
from functools import cached_property
from bson.objectid import ObjectId
from pydantic import BaseModel, field_validator, Field


class MappingType(str, Enum):
    site = "site"
    tank = "tank"
    counterparty = "counterparty"
    credential = "credential"
    product = "product"
    terminal = "terminal"
    driver = "driver"
    depot = "depot"
    trailer = "trailer"
    tractor = "tractor"
    other = "other"
    composite = "composite"


class MapType(str, Enum):
    parent = "parent"
    child = "child"


class View(str, Enum):
    grid = "grid"
    gallery = "gallery"


class CompositeMapKey(BaseModel):
    """Multi-field composite key for mapping lookups.

    A composite key allows mappings to be identified by multiple fields
    instead of a single source_id. For example, a mapping might be uniquely
    identified by (tenant, product, terminal) rather than just source_id.

    Example:
        >>> key = CompositeMapKey(key={"tenant": "acme", "product": "fuel"})
        >>> key.to_cache_key()
        '{"product":"fuel","tenant":"acme"}'
        >>> key.matches({"tenant": "acme"})
        True
    """
    model_config = {"frozen": True}

    key: dict[str, str] = Field(..., description="Field-value pairs forming the composite key")

    @field_validator('key', mode='before')
    @classmethod
    def validate_key(cls, v: dict) -> dict[str, str]:
        if not v:
            raise ValueError("Composite key cannot be empty")
        validated = {}
        for k, val in v.items():
            if not isinstance(k, str) or not k.strip():
                raise ValueError(f"Key must be non-empty string, got: {k}")
            if not isinstance(val, str):
                raise ValueError(f"Value for '{k}' must be string, got {type(val).__name__}")
            validated[k.strip()] = val
        return validated

    @cached_property
    def _cache_key_str(self) -> str:
        """Cached canonical string representation for hashing."""
        return json.dumps(self.key, sort_keys=True, separators=(',', ':'))

    def to_cache_key(self) -> str:
        """Generate a canonical string representation for caching/hashing (JSON format)."""
        return self._cache_key_str

    @classmethod
    def from_string(cls, s: str) -> Self:
        """Parse a composite key from its JSON string representation."""
        if not s:
            raise ValueError("Cannot parse empty string")
        try:
            key_dict = json.loads(s)
            if not isinstance(key_dict, dict):
                raise ValueError("Invalid format: expected JSON object")
            return cls(key=key_dict)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse composite key: {e}")

    @cached_property
    def _cached_hash(self) -> int:
        return hash(self._cache_key_str)

    def __hash__(self) -> int:
        return self._cached_hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CompositeMapKey):
            return False
        return self.key == other.key

    def __str__(self) -> str:
        return self.to_cache_key()

    def __repr__(self) -> str:
        return f"CompositeMapKey({self.to_cache_key()})"

    def __lt__(self, other: 'CompositeMapKey') -> bool:
        if not isinstance(other, CompositeMapKey):
            return NotImplemented
        return self.to_cache_key() < other.to_cache_key()

    def matches(self, partial: dict[str, str]) -> bool:
        """
        Check if this key contains all fields from the partial key.

        Returns True if all key-value pairs in partial exist in this key.
        Short-circuits on first mismatch for performance.
        """
        if len(partial) > len(self.key):
            return False
        for k, v in partial.items():
            if self.key.get(k) != v:
                return False
        return True

    def get(self, field: str, default: str | None = None) -> str | None:
        """Get a specific component from the composite key."""
        return self.key.get(field, default)

    @property
    def fields(self) -> list[str]:
        """Return the list of field names in this composite key."""
        return list(self.key.keys())


class MapBase(BaseModel):
    updated_by: str | None = Field(default="admin", description="User who last updated the mapping")
    updated_on: datetime | None = Field(default_factory=lambda: datetime.now(UTC), description="Timestamp of last update")
    type: Optional[MappingType | None] = Field(default=None, description="Type of mapping (site, tank, counterparty, etc.)")
    source_system: str | None = Field(default=None, description="External system the mapping originates from")
    is_active: Optional[bool] = Field(default=True, description="Whether the mapping is currently active")
    source_name: str | None = Field(default=None, description="Display name in the source system")
    gravitate_name: str | None = Field(default=None, description="Display name in Gravitate")
    extra_data: Optional[Dict] = Field(default=None, description="Additional metadata for the mapping")

    @field_validator('type', 'source_system', mode='before')
    @classmethod
    def validate_type_source_system(cls, v):
        if isinstance(v, str) and (v == 'nan' or v == ''):
            return None
        elif isinstance(v, float) and pd.isna(v):  # Check for actual NaN (float nan)
            return None
        return v


class Children(MapBase):
    source_id: str | None = Field(
        default=None,
        description="Source system identifier"
    )
    gravitate_id: str | None = Field(
        default=None,
        description="Gravitate identifier"
    )
    id: Optional[str] = Field(
        default_factory=lambda: str(ObjectId()),
        description="Unique identifier for this child mapping"
    )

    @field_validator('source_id', 'gravitate_id', mode='before')
    @classmethod
    def validate_identifiers(cls, v):
        if v is None or v == '' or v == 'nan':
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        return str(v)



class Map(MapBase):
    source_id: str | CompositeMapKey = Field(
        ...,
        description="Source system identifier (string or composite key)"
    )
    gravitate_id: str | CompositeMapKey = Field(
        ...,
        description="Gravitate identifier (string or composite key)"
    )
    children: Optional[list[Children]] = Field(
        default_factory=list,
        description="List of child mappings"
    )
    children_type: MappingType | None = Field(
        default=None,
        description="Type of child mappings"
    )
    owning_bucket_id: Optional[str] = Field(
        default=None,
        description="Bucket that owns this mapping"
    )
    group_id: str | None = Field(
        default=None,
        description="Group that owns this mapping"
    )


    def is_composite(self) -> bool:
        """Check if this mapping uses composite keys."""
        return isinstance(self.source_id, CompositeMapKey)

    def source_id_str(self) -> str | None:
        """Get source_id as string (for simple IDs) or None (for composite)."""
        return self.source_id if isinstance(self.source_id, str) else None

    def source_id_composite(self) -> CompositeMapKey | None:
        """Get source_id as CompositeMapKey or None (for simple IDs)."""
        return self.source_id if isinstance(self.source_id, CompositeMapKey) else None

    def gravitate_id_str(self) -> str | None:
        """Get gravitate_id as string (for simple IDs) or None (for composite)."""
        return self.gravitate_id if isinstance(self.gravitate_id, str) else None

    def gravitate_id_composite(self) -> CompositeMapKey | None:
        """Get gravitate_id as CompositeMapKey or None (for simple IDs)."""
        return self.gravitate_id if isinstance(self.gravitate_id, CompositeMapKey) else None