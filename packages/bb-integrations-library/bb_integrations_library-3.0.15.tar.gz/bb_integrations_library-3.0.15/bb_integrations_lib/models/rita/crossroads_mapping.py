from enum import Enum
from functools import lru_cache
from pprint import pprint
from types import NoneType
from typing import List, Dict, Literal, Union, override, get_args

from pydantic import BaseModel, Field

from bb_integrations_lib.models.rita.crossroads_entities import CrossroadsCompany, CrossroadsProduct, \
    CrossroadsTerminal, CrossroadsSite, CrossroadsTank, BaseCrossroadsEntity
from bb_integrations_lib.models.rita.crossroads_monitoring import CrossroadsMappingError
from bb_integrations_lib.shared.model import AgGridBaseModel


class CrossroadsMappingType(str, Enum):
    """These are the types of records we support linking. """
    location = "location"
    product = "product"
    site = "site"
    tank = "tank"
    counterparty = "counterparty"
    terminal = "terminal"

    def get_sd_collection(self):
        if self in _sd_collections:
            return _sd_collections[self]
        else:
            return None

    @classmethod
    def get_parent_types(self):
        return _sd_collections.keys()

    def get_sd_id_field(self):
        if self not in _sd_id_fields:
            return "id"
        return _sd_id_fields[self]

    def get_sd_name_field(self):
        if self not in _sd_name_fields:
            return "name"
        return _sd_name_fields[self]

_sd_collections = {
    CrossroadsMappingType.location: "location",
    CrossroadsMappingType.product: "product",
    CrossroadsMappingType.site: "store",
    CrossroadsMappingType.counterparty: "counterparty",
    CrossroadsMappingType.terminal: "location",
}

_sd_name_fields = {
    CrossroadsMappingType.tank: "tank_id",
}

_sd_id_fields = {
    CrossroadsMappingType.site: "store_number"
}


class CoreCrossroadsMapping(AgGridBaseModel):
    """
    An instance of this object associates a record in a source system to zero or more GOIDs. The data here lives only in
    client tenants, not in the master tenant database. A CrossroadsMapping may be incomplete (matches no GOIDs), exact
    (matches exactly 1 GOID), or multiple (matches 2+ GOIDs)
    """
    type: CrossroadsMappingType = Field(..., description="The type of record.")
    goids: List[str] = Field([], description="Linked CrossroadsEntities by their GOIDs. A mapping may link to multiple CrossroadsEntities.")
    display_name: str = Field(..., description="This is the friendly name of this record. It will by synced with the datasource if available.")
    source_id: str = Field(..., description="Either (1) The Mongodb ID of the item in the tenant's S&D instance, or (2) The ID of the item in the specified source system.")
    matching_info: dict = Field({}, description="This is info that we expect to use an AI agent to help us match records with CrossroadsEntities.")
    extra_data: dict = Field({}, description="Additional data that may be used by mapping logic as needed.")



class CrossroadsMapping(CoreCrossroadsMapping):
    source_system: str = Field("Gravitate Supply & Dispatch", description="The name of the system that this Mapping is for. Defaults to Gravitate Supply & Dispatch")
    children: Dict[str, CoreCrossroadsMapping] = Field({}, description="Child mappings keyed by their source_id")


class CrossroadsMappingResult(AgGridBaseModel):
    origin_tenant: str = ""
    origin_source_id: str = ""
    origin_source_system: str = ""
    origin_crossroadsmapping: CrossroadsMapping = {}
    target_tenant: str = ""
    target_crossroadsmappings: list[CrossroadsMapping] = []
    matched_crossroadsentities: dict[str, dict] = {}
    milliseconds_taken: int | None = None


class MappingRequestData(BaseModel):
    """
    The body of a mapping request. A discriminated union. There is an is_resolved field that the backend uses to know if it can look in the non-id fields for more data.

    AUTOMAGICAL: When defining a sublcass, any fields suffixed with _id will be auto-resolved by the Backend mapping methods.
    The resolved data will be put into a field of the same name without the _id. E.g. `supplier_id` and `supplier` form a
    pair that will be auto matched.
    """
    type: str
    is_resolved: bool | None = Field(default=None, description="Set 'true' by the mapping engine if all of the id fields have been resolved. This is computed by backend; user input has no effect here.")

    @classmethod
    def automap_fields(cls) -> dict[str, str]:
        """Returns a map with _id fields as the keys and full fields as the values. For use with getattr"""
        id_fields = [f for f in cls.model_fields.keys() if f.endswith("_id")]
        result = {}
        for id_field_name in id_fields:
            full_field_name = id_field_name.rstrip("_id")
            if full_field_name in cls.model_fields:
                result[id_field_name] = full_field_name
        return result

    @classmethod
    def automap_child_fields(cls) -> dict[str, str]:
        """Returns a map with _cid fields as the keys and full fields as the values. For use with getattr"""
        cid_fields = [f for f in cls.model_fields.keys() if f.endswith("_cid")]
        result = {}
        for id_field_name in cid_fields:
            full_field_name = id_field_name.rstrip("_cid")
            if full_field_name in cls.model_fields:
                result[id_field_name] = full_field_name
        return result

    @classmethod
    def get_crossroads_entity_type(cls, full_field_name: str):
        field = cls.model_fields[full_field_name]
        for arg in get_args(field.annotation):
            if arg == NoneType or issubclass(arg, CoreCrossroadsMapping):
                continue
            return arg

    def resolve_child_mappings(self, tenant: str) -> None:
        """Called after all parent mappings have been resolved. If there are children mappings, override this method and
        implement a method to fetch them from the parent mappings. This method can
        :param tenant: When an error is thrown, the provided tenant will be linked to the error.
        """
        pass

    def get_parent_mapping(self, field_name: str) -> CrossroadsMapping:
        """May be called by the mapping engine after all parent mappings are resolved. This method can be provided either
        the ID field name or the full field name of a child mapping and should return the contents of the parent mapping object."""
        pass

    def get_mapping_type_for_field(self, field_name) -> CrossroadsMappingType | None:
        """
        Called when attempting to auto-resolve multiple mappings that have different types. This is a common case, so
        we attempt to determine which data type we should use. E.g. if a crossroads entity is linked to 2 mappings, 1 site
        and 1 location, this method should provide the way to disambiguate which one this property expects based on the field.
        If the logic is more complicated than "always use this type for this mapping request" then this method is not the right
        spot to implement that info; use custom rules instead.
        """
        return None

    def access_by_property_name(self, property_name: str) -> str:
        try:
            path = property_name.split(".")
            obj = self
            for p in path:
                obj = getattr(obj, p)
            return str(obj)
        except Exception as e:
            return "<<<UNKNOWN>>>"

    @classmethod
    @lru_cache(maxsize=16)
    def outgoing_rule_properties(cls) -> list[str]:
        """
        Returns the valid rule properties for this request data when considering outgoing rules. These properties can be used in conditionals.
        Because they're restricted to outgoing rules you should return properties related to the crossroads mappings.
        """
        fields = list(cls.automap_fields().items()) + list(cls.automap_child_fields().items())
        results = []
        for _, full_field_name in fields:
            results += [f"{full_field_name}.source_id", f"{full_field_name}.display_name"]
        return results


    @classmethod
    @lru_cache(maxsize=16)
    def incoming_rule_properties(cls) -> list[str]:
        """
        Returns the valid rule properties for this request data when considering outgoing rules. These properties can be used in conditionals.
        Because they're restricted to outgoing rules you should return properties related to the crossroads mappings.
        """
        fields = list(cls.automap_fields().items()) + list(cls.automap_child_fields().items())
        results = []
        for _, full_field_name in fields:
            pydantic_field = cls.model_fields[full_field_name]
            for arg in get_args(pydantic_field.annotation):
                if arg == NoneType or issubclass(arg, CoreCrossroadsMapping):
                    continue
                props = list(arg.model_fields.keys())
                props = [p for p in props if p != "is_active" and p != "record_owner"]
                results += [f"{full_field_name}.{p}" for p in props]
        return results


class BasicMapping(MappingRequestData):
    """A basic mapping from one tenant to another. Rules are very limited here since there's very little data."""
    type: Literal["basic_mapping"] = "basic_mapping"
    obj_id: str
    obj: Union[CrossroadsMapping, BaseCrossroadsEntity, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by obj_id")
    req_type: CrossroadsMappingType | None = None

    @override
    def get_mapping_type_for_field(self, field_name) -> CrossroadsMappingType | None:
        if self.req_type is None:
            return None
        return self.req_type


class LoadPlan(MappingRequestData):
    type: Literal["load_plan"] = "load_plan"
    supplier_id: str
    product_id: str
    terminal_id: str
    destination_id: str
    destination_tank_cid: str
    supplier: Union[CrossroadsMapping, CrossroadsCompany, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by supplier_id")
    product: Union[CrossroadsMapping, CrossroadsProduct, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by product_id")
    terminal: Union[CrossroadsMapping, CrossroadsTerminal, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by terminal_id")
    destination: Union[CrossroadsMapping, CrossroadsSite, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by destination_id")
    destination_tank: Union[CoreCrossroadsMapping, CrossroadsTank, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at tank_id")


    @override
    def get_mapping_type_for_field(self, field_name) -> CrossroadsMappingType | None:
        if field_name.startswith("product"):
            return CrossroadsMappingType.product
        elif field_name.startswith("terminal"):
            return CrossroadsMappingType.terminal
        elif field_name.startswith("supplier"):
            return CrossroadsMappingType.counterparty
        elif field_name.startswith("destination_tank"):
            return CrossroadsMappingType.tank
        elif field_name.startswith("destination"):
            return CrossroadsMappingType.site
        raise ValueError(f"Invalid argument: {field_name}")

    @override
    def resolve_child_mappings(self, tenant: str) -> None:
        if self.destination_tank_cid.startswith("tank:"):
            tanks = [self.destination.children[t] for t in self.destination.children if self.destination_tank_cid in self.destination.children[t].goids and self.destination.children[t].type == CrossroadsMappingType.tank]
            if len(tanks) != 1:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for destination_tank_cid = {self.destination_tank_cid}. Could not find a unique child of site {self.destination_id} that had {self.destination_tank_cid} as its GOID. Update the child mapping on the site to link to the Crossroads entity with this GOID.",
                    error="no link to child mapping", expected_fixes=["update child mapping"], tenant=tenant,
                )
            self.destination_tank_cid = tanks[0].source_id
            self.destination_tank = tanks[0]
        else:
            self.destination_tank = self.destination.children.get(self.destination_tank_cid)
            if not self.destination_tank:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for destination_tank_cid = {self.destination_tank_cid}. There was no child with source_id {self.destination_tank_cid} for the site {self.destination_id}. Create the child mapping on the site and link it to Crossroads.",
                    error="no child mapping", expected_fixes=["create child mapping"], tenant=tenant,
                )

    @override
    def get_parent_mapping(self, field_name: str) -> CrossroadsMapping:
        if field_name.startswith("destination_tank"):
            return self.destination
        raise ValueError("Invalid argument")


class SpecificSupplyDrop(MappingRequestData):
    type: Literal["drop"] = "drop"
    product_id: str
    destination_id: str
    destination_tank_cid: str
    product: Union[CrossroadsMapping, CrossroadsProduct, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by product_id")
    destination: Union[CrossroadsMapping, CrossroadsSite, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by destination_id")
    destination_tank: Union[CoreCrossroadsMapping, CrossroadsTank, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at tank_id")

    @override
    def resolve_child_mappings(self, tenant: str) -> None:
        if self.destination_tank_cid.startswith("tank:"):
            tanks = [self.destination.children[t] for t in self.destination.children if self.destination_tank_cid in self.destination.children[t].goids and self.destination.children[t].type == CrossroadsMappingType.tank]
            if len(tanks) != 1:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for destination_tank_cid = {self.destination_tank_cid}. Could not find a unique child of site {self.destination_id} that had {self.destination_tank_cid} as its GOID. Update the child mapping on the site to link to the Crossroads entity with this GOID.",
                    error="no link to child mapping", expected_fixes=["update child mapping"], tenant=tenant,
                )
            self.destination_tank_cid = tanks[0].source_id
            self.destination_tank = tanks[0]
        else:
            self.destination_tank = self.destination.children.get(self.destination_tank_cid)
            if not self.destination_tank:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for destination_tank_cid = {self.destination_tank_cid}. There was no child with source_id {self.destination_tank_cid} for the site {self.destination_id}. Create the child mapping on the site and link it to Crossroads.",
                    error="no child mapping", expected_fixes=["create child mapping"], tenant=tenant,
                )

    @override
    def get_parent_mapping(self, field_name: str) -> CrossroadsMapping:
        if field_name.startswith("destination_tank"):
            return self.destination
        raise ValueError("Invalid argument")

    @override
    def get_mapping_type_for_field(self, field_name) -> CrossroadsMappingType | None:
        if field_name.startswith("product"):
            return CrossroadsMappingType.product
        elif field_name.startswith("supplier"):
            return CrossroadsMappingType.counterparty
        elif field_name.startswith("destination_tank"):
            return CrossroadsMappingType.tank
        elif field_name.startswith("destination"):
            return CrossroadsMappingType.site
        raise ValueError(f"Invalid argument: {field_name}")


class TSDDrop(MappingRequestData):
    type: Literal["tsd_drop"] = "tsd_drop"
    destination_id: str
    destination_tank_cid: str
    destination: Union[CrossroadsMapping, CrossroadsSite, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by destination_id")
    destination_tank: Union[CoreCrossroadsMapping, CrossroadsTank, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at tank_id")

    @override
    def resolve_child_mappings(self, tenant: str) -> None:
        if self.destination_tank_cid.startswith("tank:"):
            tanks = [self.destination.children[t] for t in self.destination.children if
                     self.destination_tank_cid in self.destination.children[t].goids and self.destination.children[t].type == CrossroadsMappingType.tank]
            if len(tanks) != 1:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for destination_tank_cid = {self.destination_tank_cid}. Could not find a unique child of site {self.destination_id} that had {self.destination_tank_cid} as its GOID. Update the child mapping on the site to link to the Crossroads entity with this GOID.",
                    error="no link to child mapping", expected_fixes=["update child mapping"], tenant=tenant,
                )
            self.destination_tank_cid = tanks[0].source_id
            self.destination_tank = tanks[0]
        else:
            self.destination_tank = self.destination.children.get(self.destination_tank_cid)
            if not self.destination_tank:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for destination_tank_cid = {self.destination_tank_cid}. There was no child with source_id {self.destination_tank_cid} for the site {self.destination_id}. Create the child mapping on the site and link it to Crossroads.",
                    error="no child mapping", expected_fixes=["create child mapping"], tenant=tenant,
                )

    @override
    def get_parent_mapping(self, field_name: str) -> CrossroadsMapping:
        if field_name.startswith("destination_tank"):
            return self.destination
        raise ValueError("Invalid argument")

    @override
    def get_mapping_type_for_field(self, field_name) -> CrossroadsMappingType | None:
        if field_name.startswith("destination_tank"):
            return CrossroadsMappingType.tank
        elif field_name.startswith("destination"):
            return CrossroadsMappingType.site
        raise ValueError(f"Invalid argument: {field_name}")


class TankReading(MappingRequestData):
    type: Literal["tank_reading"] = "tank_reading"
    site_id: str
    tank_cid: str
    site: Union[CrossroadsMapping, CrossroadsSite, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at site_id")
    tank: Union[CoreCrossroadsMapping, CrossroadsTank, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at tank_id")

    @override
    def resolve_child_mappings(self, tenant: str) -> None:
        if self.tank_cid.startswith("tank:"):
            tanks = [self.site.children[t] for t in self.site.children if self.tank_cid in self.site.children[t].goids and self.site.children[t].type == CrossroadsMappingType.tank]
            if len(tanks) != 1:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for tank_cid = {self.tank_cid}. Could not find a unique child of site {self.site_id} that had {self.tank_cid} as its GOID. Update the child mapping on the site to link to the Crossroads entity with this GOID.",
                    error="no link to child mapping", expected_fixes=["update child mapping"], tenant=tenant,
                )
            self.tank_cid = tanks[0].source_id
            self.tank = tanks[0]
        else:
            self.tank = self.site.children.get(self.tank_cid)
            if not self.tank:
                raise CrossroadsMappingError(
                    friendly_text=f"Error while resolving child mappings for tank_cid = {self.tank_cid}. There was no child with source_id {self.tank_cid} for the site {self.site_id}. Create the child mapping on the site and link it to Crossroads.",
                    error="no child mapping", expected_fixes=["create child mapping"], tenant=tenant,
                )

    @override
    def get_parent_mapping(self, field_name: str) -> CrossroadsMapping:
        if field_name.startswith("tank"):
            return self.site
        raise ValueError("Invalid argument")

    @override
    def get_mapping_type_for_field(self, field_name: str) -> CrossroadsMappingType | None:
        if field_name.startswith("site"):
            return CrossroadsMappingType.site
        elif field_name.startswith("tank"):
            return CrossroadsMappingType.tank
        raise ValueError(f"Invalid argument: {field_name}")


class OrderBasics(MappingRequestData):
    type: Literal["order_basics"] = "order_basics"
    supplier_id: str
    supplier: Union[CrossroadsMapping, CrossroadsCompany, None] = Field(default=None, description="If is_resolved == True, this will be the item pointed at by supplier_id")

    @override
    def get_mapping_type_for_field(self, field_name: str) -> CrossroadsMappingType | None:
        if field_name.startswith("supplier"):
            return CrossroadsMappingType.counterparty
        raise ValueError(f"Invalid argument: {field_name}")


class MappingRequest(BaseModel):
    """These are 'fat' mapping requests: they request backend to map multiple fields but serve as their own context for
    the rules engine."""
    origin_tenant: str
    origin_source_system: str
    target_tenant: str
    target_source_system: str

    data: Union[
        BasicMapping, LoadPlan, SpecificSupplyDrop, TSDDrop, TankReading, OrderBasics
    ] = Field(..., discriminator="type", description="The body of the mapping request. See MappingRequestData and its subclasses.")

    extra_data: dict = Field(default={}, description="Additional data that may be used by the mapping engine. Rules may also add fields here and read fields from here.")


class MappingRequestInternal(MappingRequest):
    """Holding type to differentiate from a mapping request into or out of a tenant. Has a field to mark the difference"""
    is_crossroads: Literal[True] = True


