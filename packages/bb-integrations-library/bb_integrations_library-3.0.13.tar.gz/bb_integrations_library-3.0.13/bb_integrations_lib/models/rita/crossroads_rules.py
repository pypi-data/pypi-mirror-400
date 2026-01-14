# Definitions and tech for the mapping rules engine.
from enum import Enum
from typing import Literal, runtime_checkable, Protocol

from bb_integrations_lib.models.rita.crossroads_mapping import MappingRequest
from pydantic import BaseModel, Field, model_validator, computed_field

from bb_integrations_lib.shared.model import AgGridBaseModel


class Condition(BaseModel):
    """A single condition for a property or value in a mapping rule. A rule may have many conditions."""
    property: str = Field(..., description="The property that this condition will inspect")
    predicate: Literal["equals"] = Field("equals", description="The method of comparing the property and the value.")
    value: str = Field(..., description="The value that this condition will inspect the property for, using the predicate.")


class Action(BaseModel):
    type: Literal["choose result", "inject metadata"] = Field("choose result", description="Type of action")
    value: str = Field(..., description="The value related to the type of action. This may be a GOID, a mapping ID, or a json string of metadata to provide to further mappings.")


class CrossroadsRule(AgGridBaseModel):
    """Represents rules that can describe how to resolve mappings with more than one possible resolution. Rules are either
    "incoming", "outgoing", or "override". Incoming rules describe how to choose a CrossroadsMapping when given a CrossroadsEntity.
    Outgoing rules describe how to choose a CrossroadsEntity when given a CrossroadsMapping. Override rules describe how
    to choose a CrossroadsMapping given a CrossroadsMapping, bypassing the CrossroadsEntities entirely.
    """
    display_name: str = Field("")
    type: Literal["incoming", "outgoing", "override"] = Field("incoming", description="The type of this rule. Used to choose when a rule might apply.")
    mapping_id: str | None = Field(None, description="If this rule is outgoing and related to a single mapping, then this field will be set with the DB ID of that mapping.")
    entity_goid: str | None = Field(None, description="If this rule is incoming and related to a single master entity, then this field will be set with that entity's GOID.")
    tenants: list[str] | None = Field(None, description="Which tenants this rule may apply to. If empty, can be any tenant. Must be set if type == override")
    conditions: list[Condition] = Field([], description="The match conditions that make up this rule. Logical AND: A candidate must pass all conditions.")
    action: Action = Field(..., description="The action taken by this rule when the match conditions are met.")
    conditions_mode: Literal["and", "or"] = Field(default="and", description="How should multiple conditions be applied? In AND mode the conditions will be ANDed together logically. In OR mode the conditions will be ORed together logically.")
    is_active: bool = Field(True)

    @computed_field
    @property
    def requires_properties(self) -> list[str]:
        return list({c.property for c in self.conditions})

    def can_apply(self, req: MappingRequest):
        if self.tenants is not None and len(self.tenants) > 0 and req.target_tenant not in self.tenants:
            return False
        for condition in self.conditions:
            if self.type == "outgoing" and condition.property not in req.data.outgoing_rule_properties():
                return False
            elif self.type == "incoming" and condition.property not in req.data.incoming_rule_properties():
                return False
        return True

    def meets_conditions(self, req: MappingRequest):
        if self.conditions_mode == "and":
            for condition in self.conditions:
                request_value = req.data.access_by_property_name(condition.property)
                if condition.predicate == "equals" and request_value != condition.value:
                    return False
            return True  # All conditions passed
        else:
            for conditions in self.conditions:
                request_value = req.data.access_by_property_name(conditions.property)
                if conditions.predicate == "equals" and request_value == conditions.value:
                    return True
            return False # None of the conditions were met



    @model_validator(mode="after")
    def validate(self):
        if self.mapping_id is not None and self.type != "outgoing":
            raise ValueError("`mapping_id` should only be set when type is outgoing")
        if self.entity_goid is not None and self.type != "incoming":
            raise ValueError("`entity_goid` should only be set when type is incoming")
        if not self.tenants and self.type == "override":
            raise ValueError("`tenants` must be set when type is override")
        return self


