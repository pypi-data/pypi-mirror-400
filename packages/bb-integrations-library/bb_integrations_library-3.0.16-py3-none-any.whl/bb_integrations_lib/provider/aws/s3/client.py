import json
from dataclasses import dataclass
from typing import Iterable
from json import JSONDecodeError
import boto3
from bb_integrations_lib.shared.model import RawData
from loguru import logger


@dataclass
class FileData:
    """
    Data class representing a file and its contents.

    Attributes:
        file_name (str): The name of the file.
        data (dict): The content of the file parsed as a dictionary.
    """
    file_name: str
    data: dict


class S3Client:
    """
    Client for interacting with an AWS S3 bucket, providing methods for fetching,
    archiving, and processing files.

    Attributes:
        bucket_name (str): Name of the AWS S3 bucket.
        access_key_id (str): AWS access key ID for authentication.
        secret_access_key (str): AWS secret access key for authentication.
        archive_dir (str): Directory in the bucket where files are archived.
        file_prefix (list[str]): List of file prefixes used for filtering files in the bucket.
        files_per_chunk (int): Maximum number of files to process in a single iteration.
        s3 (boto3.resource): Boto3 resource for S3 operations.
        bucket (boto3.Bucket): Boto3 bucket object for interacting with the specified S3 bucket.
    """

    def __init__(
        self,
        *,
        aws_bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_archive_dir: str,
        aws_file_prefix: list[str],
        files_per_chunk: int = 500,
    ):
        """
        Initialize the S3Client with AWS credentials and configuration.

        Args:
            aws_bucket_name (str): Name of the S3 bucket to interact with.
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            aws_archive_dir (str): Directory in the S3 bucket for archiving files.
            aws_file_prefix (list[str]): List of file prefixes for filtering files.
            files_per_chunk (int, optional): Number of files to fetch per query. Defaults to 500.
        """
        self.bucket_name = aws_bucket_name
        self.access_key_id = aws_access_key_id
        self.secret_access_key = aws_secret_access_key
        self.archive_dir = aws_archive_dir
        self.file_prefix = aws_file_prefix
        self.files_per_chunk = files_per_chunk

        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )
        self.bucket = self.s3.Bucket(name=self.bucket_name)

    def get_raw_data(self) -> Iterable[RawData]:
        """
        Fetch raw data from the S3 bucket.

        Iterates through files matching the specified prefixes, loads their contents,
        and returns them as a collection of `RawData` objects. Malformed files are
        archived and deleted from the bucket.

        Returns:
            Iterable[RawData]: An iterable containing raw data from the files.
        """
        ret = []
        for file in self._files():
            try:
                ret.append(
                    RawData(file_name=file.key, data=(json.load(file.get()["Body"])))
                )
            except JSONDecodeError:
                logger.error(f"Archiving bad file {file.key}")
                copy_source = {"Bucket": self.bucket_name, "Key": file.key}
                destination = f"{self.archive_dir}/{file.key}"
                self.bucket.copy(copy_source, destination)
                self.s3.Object(self.bucket_name, file.key).delete()
        return ret

    def archive_data(self, raw_data: RawData):
        """
        Archive a processed file in the designated archive directory of the S3 bucket.

        Args:
            raw_data (RawData): The raw data object representing the file to be archived.
        """
        copy_source = {"Bucket": self.bucket_name, "Key": raw_data.file_name}
        destination = f"{self.archive_dir}/{raw_data.file_name}"
        self.bucket.copy(copy_source, destination)
        self.s3.Object(self.bucket_name, raw_data.file_name).delete()

    def _files(self) -> Iterable:
        """
        Generate an iterable of file objects from the S3 bucket.

        Queries the S3 bucket for files matching the configured prefixes, yielding
        them in chunks defined by `files_per_chunk`.

        Returns:
            Iterable: An iterable of S3 file objects.
        """
        file_queries = [
            self.bucket.objects.filter(Prefix=prefix) for prefix in self.file_prefix
        ]
        return (
            obj for query in file_queries for obj in query.limit(self.files_per_chunk)
        )
