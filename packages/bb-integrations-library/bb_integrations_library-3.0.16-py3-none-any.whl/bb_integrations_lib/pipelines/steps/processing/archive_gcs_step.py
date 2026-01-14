import os
import uuid
from io import BytesIO

import pandas as pd
from gcloud.aio.storage import Storage
from loguru import logger

from bb_integrations_lib.models.pipeline_structs import BolExportResults
from bb_integrations_lib.protocols.pipelines import Step
from bb_integrations_lib.shared.model import RawData, FileConfigRawData


class ArchiveGCSStep(Step):
    def __init__(
            self,
            gcloud_storage: Storage,
            bucket_path: str,
            field_sep: str = ",",
            content_type: str = "",
            error_on_exists: bool = False,
            *args,
            **kwargs
    ) -> None:
        """
        Archive a file (RawData or BolExportResults) to Google Cloud Storage.
        :param gcloud_storage: A gcloud-aio-storage client.
        :param bucket_path: The bucket and optional directory to upload the file to.
          Example: "my-bucket" or "my-bucket/my-dir/my-dir-2". If a FileConfigRawData is passed to the step, the
          source_system will be appended to the directory, before the file name. (bucket/prefix/source_system/file_name)
        :param field_sep: Field separator when uploading BolExportResults.
        :param content_type: Optional - explicitly specify the content type of the file.
        :param error_on_exists: Whether to raise an exception if the file exists.
        """
        super().__init__(*args, **kwargs)

        self.storage = gcloud_storage
        self.bucket = bucket_path
        self.prefix = ""
        self.field_sep = field_sep
        self.content_type = content_type
        self.error_on_exists = error_on_exists

        if "/" in bucket_path:
            [self.bucket, self.prefix] = bucket_path.split("/", maxsplit=1)

    def describe(self):
        return "Archiving file in GCS"

    async def execute(self, i: RawData | FileConfigRawData | BolExportResults) -> RawData:
        def file_path(base_name: str):
            if isinstance(i, FileConfigRawData):
                return os.path.join(self.prefix, i.file_config.source_system, base_name)
            else:
                return os.path.join(self.prefix, base_name)

        # Will be used to change the name if a duplicate is detected.
        # Don't want to change it directly on the original object because that str will get used by later steps
        file_name = i.file_name

        if isinstance(i, BolExportResults):
            df = pd.DataFrame.from_records(i.orders)
            csv_text = df.to_csv(index=False, sep=self.field_sep)
            # Default to text/csv for BolExportResults if we don't have an explicit content type
            self.content_type = "text/csv" if not self.content_type else self.content_type
            contents = csv_text.encode("utf-8")
        else:
            contents = i.data

        if isinstance(contents, BytesIO):
            contents = contents.getvalue()

        if await self.storage.get_bucket(self.bucket).blob_exists(file_path(file_name)):
            if self.error_on_exists:
                raise Exception(f"File '{self.bucket}/{file_path(file_name)}' already exists")
            old_file_name = file_name
            file_name = f"DUPLICATE_{uuid.uuid4()}_{file_name}"
            logger.debug(
                f"Blob named '{old_file_name}' already exists; archiving '{file_name}' to GCS (backup attempt)")
        else:
            logger.debug(f"Archiving '{file_name}' to GCS")
        await self.storage.upload(self.bucket, file_path(file_name), contents or '', content_type=self.content_type)

        return i
