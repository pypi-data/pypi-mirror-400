from typing import Tuple, TypeVar, Generic, Type, Optional

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.config import GenericConfig
from bb_integrations_lib.secrets import SecretProvider
from bb_integrations_lib.shared.exceptions import ConfigNotFoundError, ConfigValidationError

T = TypeVar("T")




class PipelineWrapper(Generic[T]):
    def __init__(self,
                 bucket_name: str,
                 config_class: Type[T],
                 secret_provider: SecretProvider
                 ):
        self.bucket_name = bucket_name
        self.config_class = config_class
        self.config_name: Optional[str] = None
        self.secret_provider = secret_provider

    async def load_config(self,
                          config_name: str,
                          rita_client: GravitateRitaAPI,
                          ) -> Tuple[T, str, str]:
        """
        Load and validate configuration from Rita API.

        Returns:
            Tuple of (parsed_config, config_id, config_name)

        Raises:
            ConfigNotFoundError: If the configuration is not found
            ConfigValidationError: If the configuration fails validation
        """
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
