from datetime import datetime
from typing import Literal, Optional, Any, override, List

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from bb_integrations_lib.models.rita.issue import IssueBase


@dataclass
class CrossroadsError(Exception):
    issue: IssueBase = Field(..., description="An issue to be saved to logs")


@dataclass
class CrossroadsMappingError(Exception):
    """Custom exception type that """
    friendly_text: str = Field(..., description="User-readable text describing the error.")
    error: str = Field(..., description="Error code")
    expected_fixes: List[str] = Field(..., description="Expected fixes to the mapping problem")
    tenant: str = Field(..., description="Tenant expected to resolve the issue.")
    goid: str | None = Field(None, description="GOID of the offending crossroads entity. Usually set if the tenant needs to fix an incoming fanout.")
    mapping_source_id: str | None = Field(None, description="The source ID of the offending mapping. Usually set if the tenant needs to fix an outgoing fanout")
    mapping_source_system: str | None = Field(None, description="The source system of the offending mapping. Only if tenant != Gravitate")
    mapping_display_name: str | None = Field(None, description="The display name of the offending mapping.")


class CrossroadsLog(BaseModel):
    """A CrossroadsLog object describes the results of a crossroads operation."""
    date: datetime = Field(description="Datetime the log was filed.")
    status: Literal["succeeded", "failed", "pending", "unknown"] = Field(
        description="Status of the logged operation. Creators should specify 'succeeded' 'failed' or 'pending'",
        default="unknown")
    tenant: str = Field(description="The tenant this record exists in.")
    record_collection: str = Field(description="The DB collection this record belongs to.")
    record_id: str = Field(description="The DB ID of the relevant record. Use with record_collection to look up data.")
    record_id_field: str = Field(description="The DB field containing the record_id.")

    target_tenant: str = Field(description="The tenant that the crossroads integration was targeting.")
    target_record_collection: str | None = Field(default=None, description="The DB collection of the record in the target tenant.")
    target_record_id: str | None = Field(default=None, description="The DB ID of the record in the target tenant.")
    target_record_id_field: str | None = Field(default=None, description="The DB field containing the record_id.")

    issue_key: Optional[str] = Field(
        description="If status='failed', this should be set with a link to a Rita Issue describing the encountered problem.",
        default=None)
    issue: Optional[IssueBase] = Field(description="If status='failed', data provided here will be used to create the issue.", default=None)
    is_mapping_failure: bool = Field(False, description="True if the reason for this log being 'failed' is a mapping error. If this is true, the mapping_error property will be set.")
    mapping_error: CrossroadsMappingError | None = Field(default=None, description="Mapping error details. Set if mapping_error == True")
    success_message: Optional[str] = Field(description="If status='success', this should be set with a message to show the user.", default=None)
    success_details: Optional[dict] = Field(
        description="If status='success', this should be set with additional details related to the successful integration. E.g. set the order number", default=None)
    worker_name: str = Field(description="The name of the worker that created this log.")
    connection_id: str | None = Field(None, description="The connection that generated this log.")
    group: str | None = Field(None, description="Freeform group field; can be used as a display grouping for logs from multiple workers. E.g. 'TTE -> Caseys Crossroads' could group logs from many workers in the UI.")
    worker_request: dict | None = Field(None, description="WIP. Plan is to use this to stash the worker request on a failure for retry capabilities.")
    correlation_id: str | None = Field(default=None, description="The correlation ID for this log.")

    def is_unspecific(self) -> bool:
        """Returns true if this log is "Unspecific" and not attached to any record."""
        return self.record_id == "unknown" and self.record_collection == "unknown" and self.record_id_field == "unknown"

    @classmethod
    def create_unspecific(cls, **kwargs):
        kwargs = kwargs | {"record_id": "unknown", "record_collection": "unknown", "record_id_field": "unknown"}
        return cls(**kwargs)


class OutputCrossroadsLog(CrossroadsLog):
    correlation_id: str | None = Field(default=None, description="The correlation ID for this crossroads log.")


class MasterReferenceAudit(BaseModel):
    """A snapshot of a MasterReferenceData or MasterReferenceLink object changed at a certain time. Creation and editing an MRD will update this object."""
    document: Any = Field(description="A copy of the document as of the time of the change.")
    doc_id: str = Field(description="MongoDB ID of the document in the relevant table.")
    user: str = Field(description="The user that updated the document.")
    date: datetime = Field(description="The datetime the document was updated.")
