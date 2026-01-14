import json
import os
import uuid
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime, UTC
from functools import lru_cache
from typing import Optional, Any, Iterable, Generator
import re
import loguru
import yaml
from bson import ObjectId
from bson.raw_bson import RawBSONDocument
from loguru import logger
from pydantic import ValidationError, BaseModel
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from bb_integrations_lib.secrets.credential_models import FTPCredential, AWSCredential, GoogleCredential, IMAPCredential
from bb_integrations_lib.shared.model import CredentialType


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        return super().default(obj)

class ClientConfig(BaseModel):
    client_name: str
    client_url: str
    client_psk: str
    conn_str: str
    account_username: str = 'costco-integration'


def safe_index(file_name: str, sub_str: str, default: int = 1000) -> int:
    """
    :param file_name: file name.
    :param sub_str: sub string.
    :param default: default value.
    :return: integer index of sub_str.
    """
    if sub_str in file_name:
        return file_name.index(sub_str)
    return default


def file_time(file_name: str, sub_str: str, sep='_', strip_trailing: bool = False) -> str:
    """
    :param file_name: file name.
    :param sub_str: sub string.
    :param sep: string separator.
    :param strip_trailing: if True, strips trailing _digits pattern (e.g., _30380357).
    :return: string time of file.
    """
    if sub_str in file_name:
        start = safe_index(file_name=file_name, sub_str=sub_str) + len(sub_str)
        end = file_name.rfind(".")
        result = file_name[start:end]

        if strip_trailing:
            result = re.sub(r'_\d+$', '', result)

        if sep in result:
            return result.strip(sep)
        return result
    raise IndexError(f"SubString: {sub_str} not found on file: {file_name}")



def file_exact_match(file_name: str, sub_str: str, sep='_') -> bool:
    """
    Check if filename follows this pattern:
    - Starts with the exact substring
    - Optionally followed by separator and date
    - Ends with file extension
    - No other content before or after the substring

    Args:
        file_name: The filename to check
        sub_str: The substring to look for
        sep: The separator character (default '_')

    Returns:
        bool: True if the pattern matches, False otherwise
    """
    if not file_name or not sub_str:
        return False
    if not file_name.startswith(sub_str):
        return False
    remainder = file_name[len(sub_str):]
    if not remainder:
        return True
    if remainder.startswith('.'):
        return True
    if remainder.startswith(sep):
        date_part = remainder[1:]
        date_pattern = r'^(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{8}|\d{4}_\d{2}_\d{2}|' + \
                       r'\d{2}_\d{2}_\d{4}|\d{4}\d{2}\d{2})(\.[a-zA-Z0-9]+)?$'

        return bool(re.match(date_pattern, date_part))

    return False


def check_if_file_greater_than_date(file_name: str, sub_str: str, date_format: str,
                                    min_date: datetime = datetime.now(UTC),
                                    strip_trailing: bool = False) -> bool:
    """
    Parses a datetime out of a file name and compares it against the min_date (or current UTC, by default).

    :param file_name: File name to parse.
    :param sub_str: Prefix to strip, if found.
    :param date_format: strptime-compatible date format specifier.
    :param min_date: Date to compare the parsed date against.
      The timezone provided in this object will be used for the parsed timezone if it is not datetime aware.
    :param strip_trailing: if True, strips trailing _digits pattern (e.g., _30380357).
    :return: True if the date parsed from file_name is newer than the min_date.
    """
    try:
        file_date = file_time(file_name=file_name, sub_str=sub_str, strip_trailing=strip_trailing)
        date = datetime.strptime(file_date, date_format)
        # Check if the parsed tzinfo is naive. If so, assume it's in the same tz as min_date.
        if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
            date = date.replace(tzinfo=min_date.tzinfo)
        return date > min_date
    except IndexError as e:
        logger.error(f"Error: {e}")
        return False


def find_file_in_parent_directories(filename: str, max_levels: int = 20,
                                    secrets_folder: Optional[str] = None) -> str | None:
    """
    Searches for a file in the current directory and up to max_levels of parent directories.

    :param filename: The name of the file to search for.
    :param max_levels: The maximum number of parent directory levels to search.
    :param secrets_folder: Optional parameter defining a secrets folder name.
    :return: The full path to the file if found, else None.
    """
    current_dir = os.getcwd()
    for _ in range(max_levels):
        potential_path = os.path.join(current_dir, filename)
        if os.path.exists(potential_path):
            return potential_path
        # Check in a 'secrets' subdirectory of the current directory.
        if secrets_folder:
            potential_secrets_path = os.path.join(current_dir, secrets_folder, filename)
            if os.path.exists(potential_secrets_path):
                return potential_secrets_path
        current_dir = os.path.dirname(current_dir)
    return None


@lru_cache(maxsize=None)
def load_credentials(credential_type: str = CredentialType.ftp,
                     max_levels: int = 5,
                     secrets_folder_name: str = 'secrets') -> FTPCredential | AWSCredential | GoogleCredential | IMAPCredential:
    """
    :param credential_type: credential type.
    :param max_levels: The maximum number of parent directory levels to search for the credentials file.
    :param secrets_folder_name: The name of a secrets folder. Defaults to secrets.
    :return: Dictionary containing the credentials.
    raise:
            - ValueError if credential type is not supported.
            - FileNotFound if path is not found.
    """
    filename = f'{credential_type}.json'
    path = find_file_in_parent_directories(filename, max_levels, secrets_folder_name)

    if not path:
        logger.error(f"Credentials file not found: {filename}")
        raise FileNotFoundError(f"Credentials file not found: {filename}")

    with open(path, 'r') as file:
        json_credentials = json.load(file)

    match credential_type:
        case CredentialType.ftp:
            return FTPCredential(**json_credentials)
        case CredentialType.aws:
            return AWSCredential(**json_credentials)
        case CredentialType.google:
            return GoogleCredential(**json_credentials)
        case CredentialType.imap:
            return IMAPCredential(**json_credentials)
        case _:
            for CredentialModel in (FTPCredential, AWSCredential, GoogleCredential, IMAPCredential):
                try:
                    return CredentialModel(**json_credentials)
                except (TypeError, ValidationError):
                    continue
            raise TypeError(f'Unable to open: {filename}')


def get_client_config(base_dir: str, config_directory: str = 'deployment_configs',
                      client_name: str = 'coleman') -> ClientConfig:
    try:
        dirs = os.listdir(f'{base_dir}/{config_directory}')
        client_dir = [f for f in dirs if f == client_name][0]
        file_path = f"{base_dir}/{config_directory}/{client_dir}/env-cm.yaml"
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        file_data = data['data']
        return ClientConfig(
            client_name=client_name,
            client_url=file_data['BASE_URL'],
            client_psk=file_data['SYSTEM_PSK'],
            conn_str=build_conn_str(file_data['DB_CONNECT_STR']),
        )
    except IndexError:
        loguru.logger.error(f'Unable to find config file for {client_name}')


def build_conn_str(conn_str) -> str:
    """
    Method to build mongo conn strings w/o pri safely
    :param conn_str: original conn string
    :return: formatted conn string
    """
    if 'localhost' in conn_str:
        return conn_str
    # Determine start of cluster name
    start_cluster = safe_index(file_name=conn_str, sub_str="@") + 1
    # Determine end of cluster name
    end_cluster = safe_index(file_name=conn_str, sub_str='pri') - 1
    # Determine start of connection string
    start = 0
    # Determine end of connection string
    end = safe_index(file_name=conn_str, sub_str="@")
    cluster = conn_str[start_cluster:end_cluster]
    left = conn_str[start:end]
    if 'bbdev' in conn_str:
        return f"{left}@{cluster}.4f2iw.gcp.mongodb.net/"
    return f"{left}@{cluster}.z7gyv.mongodb.net/"


def nested_lookup(iterable: Iterable, key_path: str):
    def get_nested_value(item, path):
        parts = path.split('.')
        value = item
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
            if value is None:
                return None
        return value

    return {get_nested_value(i, key_path): i for i in iterable}


def lookup(iterable: Iterable, key: callable):
    return {key(i): i for i in iterable}


@contextmanager
def init_db(connection_str: str, db_name: str):
    from pymongo import MongoClient
    client = MongoClient(connection_str)
    db = client[db_name]
    yield db


@contextmanager
def init_db_async(connection_str: str, db_name: str):
    from pymongo import AsyncMongoClient
    client = AsyncMongoClient(connection_str)
    db = client[db_name]
    try:
        yield db
    finally:
        client.close()


def mongo_client(
        connection_string,
        read_preference='primaryPreferred',
        server_timeout_ms=60000,
        socket_timeout_ms=30000,
        connect_timeout_ms=30000,
        **kwargs
):
    """
    Args:
        connection_string: MongoDB connection URI
        read_preference: 'primary', 'primaryPreferred', 'secondary', 'secondaryPreferred', 'nearest'
        server_timeout_ms: Server selection timeout
        socket_timeout_ms: Socket timeout
        connect_timeout_ms: Connection timeout
        **kwargs: Any other MongoClient options
    """
    return MongoClient(
        connection_string,
        serverSelectionTimeoutMS=server_timeout_ms,
        socketTimeoutMS=socket_timeout_ms,
        connectTimeoutMS=connect_timeout_ms,
        readPreference=read_preference,
        retryWrites=True,
        retryReads=True,
        **kwargs
    )


def gen_lookup(db: Database, collection_name: str, find_params: dict = None, as_raw: bool = False
               ) -> dict[str, dict | RawBSONDocument]:
    """
    Generate a lookup table mapping the _id field of each document in the MongoDB collection to its data.
    :param db: An already-connected pymongo database.
    :param collection_name: The name of the collection.
    :param find_params: Optional parameters to filter the collection on, in Mongo query format
        (will be passed to collection.find).
    :param as_raw: Return RawBSONDocuments, which are decompressed on-the-fly to save resources, instead of plain dicts.
    :return: A dict where the key is the _id field of each document and the value is the whole document.
    """
    collection = db[collection_name]
    if as_raw:
        collection = collection.with_options(
            codec_options=collection.codec_options.with_options(document_class=RawBSONDocument))
    data = list(collection.find(find_params or {}))
    return {str(o['_id']): o for o in data}

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def is_uuid(s: str):
    """Returns True if string is a valid UUID."""
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


def is_valid_goid(goid: str, prefix: str):
    """Returns true if the string is a valid GOID with the specified prefix."""
    if (not goid.startswith(prefix) or not goid.split(":")[-1].isnumeric()) and not is_uuid(goid):
        return False
    return True





if __name__ == "__main__":
    credentials = load_credentials("google.credentials")
    print(credentials)
