from typing import Tuple, TypeVar, Generic, Type, Optional
from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.config import GenericConfig
from bb_integrations_lib.shared.exceptions import ConfigNotFoundError, ConfigValidationError
from bb_integrations_lib.util.config.manager import GlobalConfigManager
from bb_integrations_lib.util.config.model import GlobalConfig, ClientConstructor

T = TypeVar("T")




class PipelineWrapper(Generic[T]):
    def __init__(self,
                 tenant_name: str,
                 bucket_name: str,
                 config_class: Type[T],
                 mode: Optional[str] = "production",
                 ):
        self.tenant_name = tenant_name
        self.bucket_name = bucket_name
        self.config_class = config_class
        self.config_name: Optional[str] = None
        self.config_manager = GlobalConfigManager()
        self.mode = mode

    async def load_config(self,
                          config_name: str,
                          rita_client: GravitateRitaAPI = None,
                          ) -> Tuple[T, str, str]:
        """
        Load and validate configuration from Rita API.

        Returns:
            Tuple of (parsed_config, config_id, config_name)

        Raises:
            ConfigNotFoundError: If the configuration is not found
            ConfigValidationError: If the configuration fails validation
        """
        if not rita_client:
            rita_client = GravitateRitaAPI(
                client_id=self.secret_data.prod.rita.client_id,
                client_secret=self.secret_data.prod.rita.client_secret,
                tenant=self.tenant_name,
            )
        try:
            configs = await rita_client.get_config_by_name(
                bucket_path=self.bucket_name,
                config_name=config_name
            )
        except Exception as e:
            msg = f"Failed to retrieve config '{config_name}' from bucket '{self.bucket_name}': {e}"
            raise ConfigNotFoundError(
                msg
            ) from e

        job_config: GenericConfig = configs[config_name]

        try:
            pipeline_config: T = self.config_class.model_validate(job_config.config)
        except Exception as e:
            raise ConfigValidationError(
                f"Failed to validate config '{config_name}' as {self.config_class.__name__}: {e}"
            ) from e

        return pipeline_config, job_config.config_id, config_name

    @property
    def secret_data(self) -> GlobalConfig:
        return self.config_manager.get_environment(self.tenant_name)

    @property
    def api_clients(self) -> ClientConstructor:
        return self.config_manager.environment_from_name(self.tenant_name, self.mode)

    def __repr__(self) -> str:
        return (f"PipelineWrapper(tenant='{self.tenant_name}', "
                f"bucket='{self.bucket_name}', "
                f"type={self.config_class.__name__})")

