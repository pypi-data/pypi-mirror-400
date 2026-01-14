from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Union, Literal, Annotated, Any

from pydantic import BaseModel, Field


class UnknownRunnableException(Exception):
    pass

WorkerTaskState = Literal["sent", "received", "working", "failed", "completed"]

class WorkerRequest(BaseModel):
    """A request for a specific runnable to be executed on an available worker."""
    runnable_name: str
    runnable_kwargs: dict[str, Any] = {}
    tenant_name: str
    originator: Literal["backend", "probe", "other"] = "other"

class WorkerContentFile(BaseModel):
    """
    A file included in a worker's response. Supports binary (non-text) files by automatically encoding/decoding from
    base64 when serialized.
    """
    file_name: str
    mime_type: str | None = None
    content: bytes | None = None

    class Config:
        ser_json_bytes = "base64"
        val_json_bytes = "base64"

class WorkerResponseStatus(str, Enum):
    success = "success"
    error = "error"

class WorkerSuccessResponse(BaseModel):
    """A response from a worker indicating success and providing results."""
    # This is a pretty weird field definition. Basically, to support using this field as a discriminator for the
    # WorkerResponse union type, we need it to only ever be status="success", (or "error", in the error class).
    # These type annotations mean it is a WorkerResponseStatus that can only ever be .success, and that it cannot be set
    # in the init method (init=False) or anywhere else (init_var=True).
    # You can't use a frozen field here because it won't play nice with Beanie serialization.
    status: Annotated[Literal[WorkerResponseStatus.success], Field(init_var=True, init=False)] = WorkerResponseStatus.success
    runnable_name: str
    content: str | None = None
    content_file: WorkerContentFile | None = None
    extra_data: dict = {}

class WorkerErrorResponse(BaseModel):
    """A response from a worker indicating an error occurred and providing error details."""
    status: Annotated[Literal[WorkerResponseStatus.error], Field(init_var=True, init=False)] = WorkerResponseStatus.error
    runnable_name: str
    exception_type_name: str
    error_message: str
    reference_code: Optional[str] = None

WorkerResponse = Annotated[Union[WorkerSuccessResponse, WorkerErrorResponse], Field(discriminator="status")]


class WorkerUpdate(BaseModel):
    """Provides status updates to the requester for backgrounded tasks."""
    tenant_name: str
    originator: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    state: WorkerTaskState
    response: Optional[WorkerResponse] = None

class WorkerTask(BaseModel):
    correlation_id: str
    created_at: datetime
    updated_at: datetime
    mode: Literal["immediate", "background"]
    state: WorkerTaskState
    request: WorkerRequest
    response: Optional[WorkerResponse] = None
