from typing import Any, List, Dict, Optional

from pydantic import BaseModel

from bb_integrations_lib.models.rita.config import FileConfig, MaxSync
from bb_integrations_lib.models.rita.issue import IssueBase
from bb_integrations_lib.protocols.flat_file import Integration
from bb_integrations_lib.secrets import IntegrationSecretProvider


class StopBranch(Exception):
    pass

class StopPipeline(Exception):
    pass

class NoPipelineData(Exception):
    """
    To be raised when a pipeline step is unable to find any data to operate on.
    This would cause an error alert.
    A.K.A hard alert/exception.
    """
    pass

class NoPipelineSourceData(Exception):
    """
    To be raised when a pipeline step is unable to find any data to operate on.
    This would cause an error alert.
    A.K.A hard alert/exception.
    """
    pass

class UploadResult(BaseModel):
    succeeded: int = 0
    failed: int = 0
    succeeded_items: list = []

class BBDUploadResult(UploadResult):
    """Includes info on uploaded data """
    pass


class BolExportResults(BaseModel):
    orders: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    file_name: str
    order_number_key: str = "OrderNumber"

    @property
    def is_empty(self) -> bool:
        return len(self.orders) == 0


class PipelineContext(BaseModel):
    """
    PipelineContext is a general storage for any additional data that a step might want to add for other steps to use
    as desired. The primary use is for steps to add entries to the "included" list for process reports.

    ALL properties in this class may be unset, because only some steps will set them. If you plan to use a property to
    accomplish anything be sure to test that it has been set beforehand.
    """
    # Core pipeline tech.
    previous_output: Any = None          # this is set if a step has alt_input and wants to access the original output
    logs: List[str] = []                 # Logs captured since the last time this field was cleared.

    # issue reporting
    issues: List[IssueBase] = []

    # Process report tech.
    file_config: FileConfig | None = None  # Usually set by SFTPFileConfigStep
    included: list[dict[str, str]] = []    # Copied into the end-of-run process report, if reporting is enabled.
    included_files: dict[str, str] = {}    # Copied into the end-of-run process report, uploaded like logs to GCS
    snapshot_id: str | None = None         # Copied into the end-of-run process report, if reporting is enabled
    indexed_field: str | None = None
    extra_data: Optional[Dict] = {}
    max_sync: MaxSync | None = None
