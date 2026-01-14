import os
from typing import Any, Dict

from bb_integrations_lib.shared.model import FileReference, File
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.provider.gcp.cloud_storage.client import CloudStorageClient


class GCSExportFileStep(Step[Any, Any, None]):
    def __init__(self, step_configuration: Dict[str, str]) -> None:
        super().__init__(step_configuration)
        self.gcs_client = CloudStorageClient()
        self.bucket = step_configuration['bucket']

    def describe(self) -> str:
        return "Exporting file to GCS bucket"

    async def execute(self, i: FileReference) -> FileReference:
        file_name = os.path.basename(i.file_path)
        with open(i.file_path, "rb") as f:
            file_data = f.read()
        file = File(
            file_name=file_name,
            file_data=file_data
        )
        try:
            self.gcs_client.upload_file(file, self.bucket)
            return i
        except FileExistsError:
            # If run twice and the file was already archived, we don't need to archive another copy.
            return i
        except Exception as e:
            raise e

