from typing import Any, Dict, Optional, Self
from enum import Enum
from pydantic import BaseModel
from datetime import datetime, UTC

class ReferenceDataType(str, Enum):
    terminal = "terminal"
    store = "store"
    tank = "tank"
    location = "location"
    product = "product"
    counterparty = "counterparty"


class CoreMasterReferenceData(BaseModel):
    """
    A single 'item' in the industry. This could point to a store, a product, a company, or anything else.
    The data here lives in the RITA master tenant only, and works in conjunction with the data stored in RITA client
    tenant's tables to enable conversion from one client's representation to another.
    """
    data_type: ReferenceDataType
    """The data type of this item. Used for lookups."""

    mrid: str
    """The unique ID of this item. MasterReferenceLink objects will link on this field."""

    name: str
    """Display name of this item."""

    source_tenant: str | None = None
    """The original tenant of this item, if it has one."""

    matching_info: Dict[str, Any] = {}
    """A dictionary describing the info that makes this object unique. E.g. for terminals this could be the federal TCN."""
    # We plan to engineer some way to throw a client's data at an LLM for matching. Matching_info would be the place to store
    # data that's similar in structure.

    mrd_extra_data: Dict[str, Any] = {}
    """Any additional data about the object that should be tied to it during the conversion process."""

    updated_by: Optional[str] = None
    updated_on: Optional[datetime] = datetime.now(UTC)


class MasterReferenceData(CoreMasterReferenceData):
    children: Dict[str, CoreMasterReferenceData] = {}
    """The children of this master reference data"""


class CoreMasterReferenceLink(BaseModel):
    """
    Links 'items' in this tenant's gravitate instance to the MasterReferenceData. The data here lives only in RITA client
    tenants, not the RITA master tenant, and matches some record in the MasterReferenceData. It is possible for one
    MasterReferenceLink to match one MasterReferenceData.
    """
    data_type: ReferenceDataType
    """The data type of this item. Used for lookups."""

    mrid: Optional[str] = None
    """Linked MasterReferenceData item. This may be empty and indicates that there is no associated item."""

    display_name: str
    """
    Display name of this item, in the context of the tenant's gravitate. This is not used for code lookups and can be
    set to anything. It may be set automatically by the sync module, if the source_system is "Gravitate"
    """

    source_id: str
    """
    Either (but not both): 
      - Mongodb ID of the item in the tenant's gravitate (if source_system is "Gravitate").
      - ID of the item in the specified source system.
    """

    matching_info: Dict[str, Any] = {}
    """A dictionary describing the info that makes this object unique. E.g. for terminals this could be the federal TCN, or an address."""

    mrl_extra_data: Dict[str, Any] = {}
    """Any additional data about the object that should be tied to it during the conversion process."""


    updated_by: Optional[str] = None
    updated_on: Optional[datetime] = datetime.now(UTC)


class MasterReferenceLink(CoreMasterReferenceLink):
    source_system: str = "Gravitate"
    """The source system of this item. Defaults to 'Gravitate'. Used in mapping requests to add detail in mappings."""

    children: Dict[str, CoreMasterReferenceLink] = {}
    """Child references keyed by their Source ID. These can only match child references of the parent's matched master
    reference data."""


class ReferenceDataMappingExtraData(BaseModel):
    origin_mrl_extra_data: dict[str, Any] = {}
    mrd_extra_data: dict[str, Any] = {}


class ReferenceDataMapping(BaseModel):
    origin_source_id: str = ""
    origin_source_system: str = ""
    origin_mrl_id: str | None = None
    origin_tenant: str = ""
    target_tenant: str | None = None
    target_mrls: list[MasterReferenceLink] = []
    matched_mrid: str | None = None
    matched_child_mrid: str | None = None
    extra_data: ReferenceDataMappingExtraData = ReferenceDataMappingExtraData()
    milliseconds_taken: int | None = None
