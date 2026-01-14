from typing import Optional, Union

from pydantic import BaseModel, Field

from bb_integrations_lib.models.enums import ProbeEventType
from bb_integrations_lib.models.probe.request_data import RequestData, CreateOrderFromSDOrder, UpdateStatusFromSD, \
    CancelOrderFromSD, SaveBOLsAndDropsFromSD, ErrorRequestData, MacropointLocationUpdate


class ProbeEvent(BaseModel):
    source_probe: str
    type: ProbeEventType
    timestamp: str  # Datetime in ISOformat, UTC
    data: Union[CreateOrderFromSDOrder, UpdateStatusFromSD, CancelOrderFromSD, SaveBOLsAndDropsFromSD, ErrorRequestData, MacropointLocationUpdate] = Field(discriminator="request_type")

    record_id: Optional[str] = Field(description="The DB ID of the relevant record picked up by the probe. Must be set for all Crossroads operations.", default=None)
    record_id_field: Optional[str] = Field(description="The DB field containing the record_id. Must be set for all Crossroads operations.", default=None)
    record_collection: Optional[str] = Field(description="The DB collection this record belongs to. Must be set for all Crossroads operations.", default=None)


