import os

from gcloud.aio.storage import Storage
from loguru import logger

from bb_integrations_lib.shared.model import FileReference
from bb_integrations_lib.protocols.pipelines import Step


class GCSExportFileStep(Step):
    def __init__(
            self,
            gcloud_storage: Storage,
            bucket: str,
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.storage = gcloud_storage
        self.bucket = bucket

    def describe(self) -> str:
        return "Exporting file to GCS bucket"

    async def execute(self, i: FileReference) -> FileReference:
        file_name = os.path.basename(i.file_path)
        with open(i.file_path, "rb") as f:
            file_data = f.read()

        if await self.storage.get_bucket(self.bucket).blob_exists(file_name):
            # If run twice and the file was already archived, we don't need to archive another copy.
            logger.debug(f"Blob '{file_name}' already exists in bucket '{self.bucket}', skipping upload")
            return i

        await self.storage.upload(self.bucket, file_name, file_data)
        return i
