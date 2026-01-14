from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class AuthType(str, Enum):
    no_auth = "no auth"
    bearer_with_username = "bearer with username and password"
    bearer_with_clientid = "bearer with client id"

class ProbeSubscriber(BaseModel):
    id: str | None = None
    url: str | None = None
    auth_url: str | None = None
    username: str | None = None
    password: str | None = None
    psk: str | None = None
    auth_type: AuthType = AuthType.no_auth
    is_active: bool = True

class WorkerTarget(BaseModel):
    worker_name: str | None = None
    kwargs: dict | None = None

class ProbeConfig(BaseModel):
    probe_id: str | None = None
    is_active: bool = True
    report_create: bool = False
    report_delete: bool = False
    report_update: bool = False
    conn_str: str | None = None
    database: str | None = None
    collection: str | None = None
    query: dict = {} # Events will only be reported if the object passes this filter.
    entity_field: str | None = None
    resume_token: str | None = None
    update_check_interval_minutes: int = 0  # 0 implies a keep-alive probe that will always run.
    external_subscribers: list[ProbeSubscriber] = []
    worker_targets: list[WorkerTarget] = []  # List of RITA-owned workers to notify.
    sending_entity_type: str | None = None
    probe_type: str = "StandardProbe"  # The type of probe to be run on this config. Usually "StandardProbe"
    resume_token_write_interval_seconds: int = 0  # At least this many seconds must pass before the resume token is written.
    args: dict = {}  # arguments for custom probes.
    probe_args: dict = {}
    mode: Literal["test", "prod"] = "test"
    output_request_data: str | None = None


class ProbeStats(BaseModel):
    time_started: str | None = None
    changes_seen: int = 0
    changes_processed: int = 0
    num_times_updated_resume_token: int = 0
    resume_token_time: str | None = None  # The timestamp that was associated with the last resume token updated. If the probe fell behind and is catching up, this may be significantly in the past.
    resume_token_update_time: str | None = None  # The actual wall clock time when the resume token was last updated.
    extra_data: dict = {}
