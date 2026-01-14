from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, Field


class JobLocation(BaseModel):
    external_id: str
    name: str
    address: str
    latitude: str
    longitude: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    country_code: str = Field(min_length=2, max_length=2)
    postal_code: str | None = None
    postal_splc:  str | None = None
    time_zone: Literal["US/Pacific", "US/Arizona", "US/Mountain", "US/Central", "US/Eastern"] | None = None

class JobTaskAppointment(BaseModel):
    start_time: datetime
    end_time: datetime
    ready_time: datetime
    late_time: datetime | None = None

class JobTask(BaseModel):
    # external_data: JobTaskExternalData
    remarks: list[str]
    fields: dict[str, str]
    id: str
    external_id: str
    order: int = Field(description="Index of the task within the step.")
    type: str
    status: str
    name: str
    completed: bool
    completed_at: datetime | None = None
    assets: str | None = None

class JobStep(BaseModel):
    tasks: list[JobTask]
    order: int = Field(description="Index of the step within the job.")
    type: str
    name: str
    external_id: str
    location_external_id: str
    completed: bool
    completed_at: datetime | None = None
    is_disabled: bool | None = None
    is_bypassable: bool | None = None
    is_bypassed: bool | None = None
    bypass_reason: str | None = None
    is_reorderable: bool | None = None
    reorder_reason: str | None = None
    is_skippable: bool | None = None
    is_skipped: bool | None = None
    skip_reason: str | None = None

class ValueWithUnit(BaseModel):
    value: float
    uom: str

class ShipmentDetails(BaseModel):
    total_distance: ValueWithUnit

class JobDefinition(BaseModel):
    status: str  # TODO: What statuses are possible?
    external_id: str
    locations: list[JobLocation]
    steps: list[JobStep]
    shipment_details: ShipmentDetails

class LoadEntity(BaseModel):
    type: Literal["trailer", "bill_of_lading"]
    value: str

class LoadDefinition(BaseModel):
    start_date: date
    end_date: date
    load: str | None = None
    user_external_id: str
    entities: list[LoadEntity]
