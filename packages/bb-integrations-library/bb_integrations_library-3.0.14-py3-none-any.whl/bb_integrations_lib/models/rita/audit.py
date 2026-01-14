from pydantic import BaseModel, Field
from datetime import datetime, UTC, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum

class ProcessReportBase(BaseModel):
    created_on: datetime = datetime.now(UTC)
    indexed_field: str
    included: Optional[List[Dict[str, str]]] = []
    config_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    logs: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True

class ProcessReportV2Status(str, Enum):
    start = "start" # while start -> in progress = True
    stop = "stop" # means halt
    error = "error" #  full failure
    partial = "partial" # partial success

    @property
    def in_progress(self) -> bool:
        return self == ProcessReportV2Status.start

class ProcessReportFileReference(BaseModel):
    file_base_name: str = None
    created_on: Optional[datetime] = datetime.now(UTC)
    status: Optional[ProcessReportV2Status] = None


class UploadProcessReportFile(BaseModel):
    file_base_name: str
    content: str


class ProcessReportBaseV2(BaseModel):
    # This doesn't seem to conflict with Beanie's internal _id field, but it allows us to deserialize an _id coming
    # from rita-backend.
    id: Optional[str] = Field(None, frozen=True, alias="_id")
    trigger: str
    status: Optional[ProcessReportV2Status] = ProcessReportV2Status.start
    config_id: Optional[str] = None
    updated_on: Optional[datetime] = datetime.now(UTC)
    created_on: Optional[datetime] = datetime.now(UTC)
    logs: Optional[List[ProcessReportFileReference]] = []
    included_files: Optional[List[ProcessReportFileReference]] = []

    @property
    def time_delta(self) -> timedelta:
        return self.updated_on - self.created_on

    class Config:
        arbitrary_types_allowed = True


class CreateReportV2(BaseModel):
    """
    Used for creating a process report with a Rita endpoint.
    :param bool alert_override: Whether to override (force) send an alert.
    """
    alert_override: bool = False
    trigger: str
    status: Optional[ProcessReportV2Status] = ProcessReportV2Status.start
    config_id: Optional[str] = None
    log: Optional[UploadProcessReportFile] = None
    included_files: Optional[list[UploadProcessReportFile]] = None


class UpdateReportV2(BaseModel):
    """Used for updating an already-created report with a Rita endpoint."""
    report_id: str
    alert_override: bool = False
    log: Optional[UploadProcessReportFile] = None
    included_files: Optional[list[UploadProcessReportFile]] = None
    status: ProcessReportV2Status = None


    @property
    def in_progress(self) -> bool:
        return self == ProcessReportV2Status.start


class ProcessReportResponseV2(ProcessReportBaseV2):
    logs: Optional[List[str]] = None


class NotificationChannel(str, Enum):
    email = "email"
    slack = "slack"


class NotificationStatus(str, Enum):
    sent = "sent"  # email has been sent
    pending = "pending"  # alert is yet to be sent
    passed = "pass"  # alert is not needed
    alert = "alert"  # alert the UI


class Notification(BaseModel):
    notification_status: NotificationStatus = NotificationStatus.pending
    updated_on: datetime = datetime.now(UTC)
    channel: NotificationChannel = NotificationChannel.email
    recipients: Optional[list] = None


class AlertBase(BaseModel):
    config_id: Optional[str] = None
    process_id: Optional[str] = None
    trigger: Optional[str] = None
    created_on: Optional[datetime] = datetime.now(UTC).replace(tzinfo=UTC)
    notification: Notification = Notification()
