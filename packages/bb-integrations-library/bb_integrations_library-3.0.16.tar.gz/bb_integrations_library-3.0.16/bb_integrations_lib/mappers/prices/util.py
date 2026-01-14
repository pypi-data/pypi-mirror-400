from typing import Union, Protocol, runtime_checkable

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI, RitaBackendAPI
from bb_integrations_lib.mappers.prices.model import IntegrationType, PricingIntegrationConfig
from bb_integrations_lib.mappers.prices.protocol import ExternalPriceMapperIntegration
from bb_integrations_lib.provider.sqlserver.client import SQLServerClient
from bb_integrations_lib.util.config.model import GlobalConfig


@runtime_checkable
class PricingIntegrationGetterProtocol(Protocol):
    def get_integration_mapping_client_by_entity(self, entity_key: str) -> Union[
        ExternalPriceMapperIntegration, RitaBackendAPI]:
        """Gets integration by entity key."""

    def init_class(self, integration_type: IntegrationType) -> Union[
        ExternalPriceMapperIntegration, RitaBackendAPI]:
        """Initializes integration class given a key"""


class PricingIntegrationGetter:
    def __init__(
            self,
            config: PricingIntegrationConfig
    ):
        self.config: PricingIntegrationConfig = config
        self.entity_config = config.entity_config
        self.client_secret: GlobalConfig = self.config_manager.get_environment(config.environment)

    def get_integration_mapping_client_by_entity(self, entity_key: str) -> Union[
        ExternalPriceMapperIntegration, RitaBackendAPI]:
        try:
            integration_type = self.entity_config.get(entity_key).mapping_integration.type
            if integration_type is None:
                raise KeyError(f"No integration type found for entity key: {entity_key}")
            client_class = self.init_class(integration_type)
            if client_class is None:
                raise KeyError(f"No client class found for integration type: {integration_type}")
            return client_class
        except KeyError as e:
            raise NotImplementedError(str(e))

    def init_class(self, integration_type: IntegrationType) -> Union[
        ExternalPriceMapperIntegration, RitaBackendAPI]:
        if integration_type == IntegrationType.sql:
            return SQLServerClient(
                server=self.client_secret.extra_data.get("server"),
                database=self.client_secret.extra_data.get("database"),
                username=self.client_secret.extra_data.get("username"),
                password=self.client_secret.extra_data.get("password"),
            )
        if integration_type == IntegrationType.rita:
            return GravitateRitaAPI(
                client_id=self.client_secret.prod.rita.client_id,
                client_secret=self.client_secret.prod.rita.client_secret,
                tenant=self.config.environment
            )
        else:
            raise NotImplementedError(f"Integration type {integration_type} is not supported")

