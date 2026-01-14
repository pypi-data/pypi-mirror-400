import time
import urllib.parse
from os import getenv
from typing import TypeVar

import onepasswordconnectsdk as opc_sdk
from loguru import logger
from onepasswordconnectsdk.client import AsyncClient as OpConnectAsyncClient
from pydantic.v1 import ValidationError

from bb_integrations_lib.secrets import BadSecretException, AnyCredential
from bb_integrations_lib.secrets.adapters import OPSecretAdapter

T = TypeVar("T", bound=AnyCredential)


class SecretProvider:
    """
    Provides secrets from a 1Password Connect vault. Getting an index of vault items is cached for cache_ttl, but
    individual vault items are retrieved fresh in every call to get_secret.
    """

    def __init__(self, op_connect_host: str, op_token: str, vault_name: str, cache_ttl: int = 60):
        self._op_host = op_connect_host
        self._op_token = op_token
        self._op_client: OpConnectAsyncClient | None = None
        self._vault = None
        self._item_overview = []
        self._item_overview_refreshed = 0
        self.vault_name = vault_name
        self.cache_ttl = cache_ttl

    async def _get_client(self) -> OpConnectAsyncClient:
        if self._op_client:
            return self._op_client
        else:
            self._op_client = opc_sdk.new_client(
                url=self._op_host,
                token=self._op_token,
                is_async=True,
            )
            await self.use_vault(self.vault_name)
            return self._op_client

    async def _refresh_item_overviews(self) -> None:
        self._item_overview = await (await self._get_client()).get_items(self._vault.id)
        self._item_overview_refreshed = time.monotonic()

    async def use_vault(self, vault_name: str):
        self.vault_name = vault_name
        self._vault = await self._op_client.get_vault_by_title(self.vault_name)
        await self._refresh_item_overviews()

    async def get_item_overviews(self) -> list[opc_sdk.models.SummaryItem]:
        """
        Return a list of overview items in the vault. Refreshes the list from 1P if the cached version has expired.
        """
        if time.monotonic() - self._item_overview_refreshed > self.cache_ttl:
            await self._refresh_item_overviews()
        return self._item_overview

    async def get_secret_plain(self, item_name: str) -> dict:
        """
        Retrieves a secret from 1Password and returns it as a dict of fields, with the standard transformations applied.
        See documentation for ``OPSecretAdapter.opc_to_credential_dict`` for details on the transformations.

        :param item_name: The name of the secret to load.
        :return: A dictionary of field_name:value for all fields in the secret.
        """
        c = await self._get_client()
        item = await c.get_item_by_title(urllib.parse.quote(item_name), self._vault.id)

        return OPSecretAdapter.opc_to_credential_dict(item)

    async def get_secret(self, item_name: str, secret_type: type[T]) -> T:
        """
        Retrieves a secret from 1Password and tries to load it as a Pydantic model of type ``T``.

        Model initialization is handled by Pydantic; it's recommended that the model 'ignore' ``extra`` fields
        (the default) to avoid notes or other extra fields in the 1Password item from causing validation errors. The
        model is initialized by a call roughly equivalent to ``T({field_name:value,...})`` for all fields present in the
        1Password secret.

        Note: If there are spaces in the 1Password field names, they will be replaced with underscores.

        :param item_name: The name of the secret to load.
        :param secret_type: The type of secret to load, or a TypeAdapter of a discriminated union. Must be derived from
          Pydantic BaseModel.
        :raises BadSecretException: If the secret loads successfully but cannot be parsed as the expected type.
        :return: An instance of ``T`` with the fields from the secret loaded.
        """
        try:
            c = await self._get_client()
            item = await c.get_item_by_title(urllib.parse.quote(item_name), self._vault.id)
            return OPSecretAdapter.opc_to_credential(item, secret_type)
        except ValidationError:
            raise BadSecretException(f"Failed to parse secret {item_name} as type({secret_type})")


class IntegrationSecretProvider(SecretProvider):
    """A SecretProvider with defaults appropriate for integration pipelines."""

    def __init__(
            self,
            op_connect_host: str,
            vault_name: str,
            op_token_env_var: str = "OP_SERVICE_ACCOUNT_TOKEN",
            op_token_override: str | None = None,
    ):
        self.op_connect_host = op_connect_host
        self.vault_name = vault_name

        # 3 ways to get the 1P token:
        # 1. If op_token_override is provided, use that.
        # 2. If op_token_env_var is set, use that.
        # 3. If a file named .1ptoken, is next to the script or in the parent dir, use that.

        if op_token_override:
            op_token = op_token_override
            logger.warning(
                f"Initializing IntegrationSecretProvider with provided op_token_override on vault '{vault_name}'"
            )
        else:
            # Try to load the token from the environment variable
            op_token = getenv(op_token_env_var)

            if op_token:
                logger.info(
                    f"Initializing IntegrationSecretProvider with token from env variable '{op_token_env_var}' "
                    f"on vault '{vault_name}'"
                )
            else:
                op_token = self._find_token_in_file()
                if op_token:
                    logger.info(
                        f"Initializing IntegrationSecretProvider with token from .1ptoken file "
                        f"on vault '{vault_name}'"
                    )
                if not op_token:
                    raise ValueError(
                        f"No op_token_override provided, env variable '{op_token_env_var}' not set,and a .1ptoken file "
                        "is not found; cannot load secrets"
                    )

        super().__init__(
            op_connect_host=op_connect_host,
            op_token=op_token,
            vault_name=self.vault_name
        )

    @staticmethod
    def _find_token_in_file() -> str | None:
        paths_to_try = ["../.1ptoken", ".1ptoken"]
        for path in paths_to_try:
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except FileNotFoundError:
                pass
        return None
