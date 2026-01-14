from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Union, Dict, Any, List

from pydantic import BaseModel, ValidationError, model_validator, Field, ConfigDict

from bb_integrations_lib.models.rita.probe import ProbeConfig


class MaxSync(BaseModel):
    """
    This class tracks the most recent synchronization timestamp for a job config
    along with additional contextual information needed for resuming sync operations.

    Attributes:
        max_sync_date (datetime): The timestamp of the most recent successful
            synchronization. Defaults to the current UTC time. Serves as a checkpoint
            to determine where to resume data synchronization from in later
            sync operations.
        context (dict): Key-value pairs storing additional synchronization context.
            Can contain resume tokens, sync IDs, cursors, batch sizes, source versions,
            retry counts, and other custom metadata specific to the job run.

    Example:
        >>> sync_info = MaxSync(
        ...     max_sync_date=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        ...     context={
        ...         "resume_token": "abc123xyz",
        ...         "sync_id": "sync_2024_001",
        ...         "batch_size": 1000
        ...     }
        ... )
    """

    max_sync_date: datetime = datetime.now(UTC)
    context: Optional[Dict] = None


class ConfigType(str, Enum):
    template = "template"
    process = "process"
    generic = "generic"
    fileconfig = "fileconfig"
    probeconfig = "probeconfig"
    DEPRECATED_crossroadsconfig = "crossroadsconfig"
    DEPRECATED_connectorconfig = "connectorconfig"
    scheduler = "scheduler"


class SchedulerJob(BaseModel):
    enabled: bool = False
    name: str
    job_func: str = Field(description="The function from the scheduler module to run")
    trigger: str = Field(description="The name of the APScheduler trigger to use for this job")
    scheduler_kwargs: Optional[dict[str, Any]] = Field({},
                                                       description="To pass to the APScheduler job creation function")
    job_kwargs: Optional[dict] = Field({}, description="To pass to the scheduled function")


class SchedulerConfig(BaseModel):
    enabled: bool = False
    jobs: list[SchedulerJob] = []


class Alert(BaseModel):
    enabled: Optional[bool] = False
    tolerance: Optional[int] = None
    notification: Optional[bool] = False
    distribution_list: Optional[list[str]] = None


class ConfigAction(str, Enum):
    concat = "concat"
    parse_date = "parse_date"
    concat_date = "concat_date"
    add = "add"
    copy = "copy"
    remove_leading_zeros = "remove_leading_zeros"
    remove_trailing_zeros = "remove_trailing_zeros"
    wesroc_volume_formula = "wesroc_volume_formula"
    blank = ""


class FileConfigColumn(BaseModel):
    column_name: str
    file_columns: list[str]
    action: ConfigAction | None = None  # "None" is implicitly a copy action.
    format: str | None = None


class FileConfig(BaseModel):
    """Configuration information that details how a file should be processed."""
    client_name: str = ""
    file_name: str = ""
    file_extension: str = 'csv'
    separator: str = ''
    cols: list[FileConfigColumn] = []
    source_system: str = ""
    inbound_directory: str = ""
    archive_directory: str = ""
    date_format: str = ""
    config_id: Optional[str] = Field(default=None,
                                     exclude=True)  # Placeholder to stuff the parent config ID when needed.


class Config(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    created_by: str
    created_on: datetime = datetime.now(UTC)
    updated_on: datetime = datetime.now(UTC)
    updated_by: Optional[str] = None
    type: ConfigType
    owning_bucket_id: Optional[str] = None
    password_fields: Optional[list[str]] = None
    config: Union[Dict[str, Any], List[Any]]
    alert: Optional[Alert] = Alert()
    max_sync: Optional[MaxSync] = None

    # I hate this. A config is not necessarily an integration. An Integration can have a config.
    # We should instead model the Integration/Connection to contain max_sync or something like it.
    # TODO: speak with Ben/Nick
    model_config = ConfigDict(populate_by_name=True)


    @model_validator(mode='before')
    @classmethod
    def ensure_alert_is_not_none(self, values):
        if isinstance(values, dict):
            if values.get("alert") is None:
                values["alert"] = Alert()
        return values

    def validate_type(self) -> bool:
        if self.type == "generic":
            return True

        if self.type == "fileconfig":
            try:
                FileConfig(**self.config)
                return True
            except ValidationError as e:
                print(e)
                return False

        if self.type == "probeconfig":
            try:
                ProbeConfig(**self.config)
                return True
            except ValidationError as e:
                print(e)
                return False

        if self.type == "scheduler":
            try:
                SchedulerConfig(**self.config)
                return True
            except ValidationError as e:
                print(e)
                return False
        return True

    def get_config_value(self):
        if self.type == "generic":
            return self.config

        if self.type == "fileconfig":
            return FileConfig(**self.config)


class GenericConfig(BaseModel):
    config_id: str
    config: Any

    class Config:
        arbitrary_types_allowed = True


if __name__ == "__main__":
    doc = {
        "name": "Test Config",
        "created_by": "user123",
        "type": "fileconfig",
        "config": {}
    }

    config = Config(**doc)
    print(config.alert)
