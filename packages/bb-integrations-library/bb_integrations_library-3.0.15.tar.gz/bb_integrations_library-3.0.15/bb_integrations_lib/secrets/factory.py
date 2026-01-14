import functools

from io import StringIO
from loguru import logger
from typing import TypeVar

from gcloud.aio.auth import Token
from gcloud.aio.storage import Storage
from pymongo import MongoClient, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.gravitate.pe_api import GravitatePEAPI
from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
from bb_integrations_lib.provider.api.keyvu.client import KeyVuClient
from bb_integrations_lib.provider.api.quicktrip.client import QTApiClient
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.provider.imap.client import IMAPClient
from bb_integrations_lib.secrets import SecretProvider, AnyCredential, IMAPCredential
from bb_integrations_lib.secrets.credential_models import FTPCredential, GoogleCredential, MongoDBCredential, \
    KeyVuCredential

T = TypeVar("T", bound=BaseAPI)


def _log_creation(func):
    async def log(self, secret_name: str, *args, **kwargs):
        ret = await func(self, secret_name, *args, **kwargs)
        if self.log_creations:
            logger.debug(f"Made {type(ret).__name__} from '{secret_name}'")
        return ret
    return log


class APIFactory:
    """Builds API or client instances from named secrets using a SecretProvider."""

    def __init__(self, provider: SecretProvider, log_creations: bool = True):
        self.provider = provider
        self.log_creations = log_creations

    async def _make(self, secret_name: str, api: type[T]) -> T:
        return api.from_credential(await self.provider.get_secret(secret_name, AnyCredential))

    @_log_creation
    async def sd(self, secret_name: str) -> GravitateSDAPI:
        return await self._make(secret_name, GravitateSDAPI)

    @_log_creation
    async def rita(self, secret_name: str) -> GravitateRitaAPI:
        return await self._make(secret_name, GravitateRitaAPI)

    @_log_creation
    async def pe(self, secret_name: str) -> GravitatePEAPI:
        return await self._make(secret_name, GravitatePEAPI)

    @_log_creation
    async def ftp(self, secret_name: str) -> FTPIntegrationClient:
        return FTPIntegrationClient(await self.provider.get_secret(secret_name, FTPCredential))

    @_log_creation
    async def gcloud_storage(self, secret_name: str) -> Storage:
        secret = await self.provider.get_secret(secret_name, GoogleCredential)
        as_json = secret.model_dump_json()
        return Storage(
            token=Token(
                service_file=StringIO(as_json),
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        )

    @_log_creation
    async def mongo_db(self, secret_name: str) -> AsyncDatabase:
        secret = await self.provider.get_secret(secret_name, MongoDBCredential)
        return AsyncMongoClient(secret.mongo_conn_str)[secret.mongo_db_name]

    @_log_creation
    async def imap(self, secret_name: str) -> IMAPClient:
        return IMAPClient(await self.provider.get_secret(secret_name, IMAPCredential))

    @_log_creation
    async def qt(self, secret_name: str) -> QTApiClient:
        return await self._make(secret_name, QTApiClient)

