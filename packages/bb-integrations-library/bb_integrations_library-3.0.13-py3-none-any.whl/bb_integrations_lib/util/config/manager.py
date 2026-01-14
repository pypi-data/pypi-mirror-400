import json
from loguru import logger
from typing import Dict, Optional, Any

from bb_integrations_lib.mappers.prices.protocol import PriceMapperProtocol
from bb_integrations_lib.shared.model import File
from bb_integrations_lib.util.config.model import GlobalConfig, Configs, Config, ClientConstructor, Client
from bb_integrations_lib.provider.gcp.cloud_secrets.client import CloudSecretsClient


# Base Exception class for GlobalConfigManager
class GlobalConfigException(Exception):
    """Base exception class for GlobalConfigManager operations."""
    pass


# Environment-related exceptions
class EnvironmentException(GlobalConfigException):
    """Base exception class for environment-related operations."""
    pass


class EnvironmentAlreadyExistsException(EnvironmentException):
    """Raised when trying to create an environment that already exists."""
    pass


class EnvironmentDoesNotExistException(EnvironmentException):
    """Raised when trying to access an environment that does not exist."""
    pass


# Config-related exceptions
class ConfigException(GlobalConfigException):
    """Base exception class for configuration-related operations."""
    pass


class ConfigAlreadyExistsException(ConfigException):
    """Raised when trying to create a config that already exists."""
    pass


class ConfigDoesNotExistException(ConfigException):
    """Raised when trying to access a config that does not exist."""
    pass


class GlobalConfigManager:
    """Manages global configurations for clients/customers stored in Google Cloud Secret Manager.

    This class provides an interface to create, retrieve, update, and delete
    client-specific configuration data in a centralized location. Each client
    (referred to as an "environment") has its own dedicated configuration space
    within a single Google Cloud Secret.

    All environment names are automatically converted to lowercase for consistency.
    """

    def __init__(self, file_name_override: Optional[str] = None):
        """Initialize the manager with a file name.

        Args:
            file_name_override: Custom file name for the configuration.
                Defaults to "global_integration_configurations".
        """
        self.file_name = file_name_override or "global_integration_configurations"

    def environment_from_name(self, environment_name: str, env_mode: str, sd_basic_auth: bool = False) -> ClientConstructor:
        from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
        from bb_integrations_lib.gravitate.sd_api import GravitateSDAPI
        from bb_integrations_lib.gravitate.pe_api import GravitatePEAPI
        from bb_integrations_lib.util.config.model import GlobalConfig, ClientConstructor, Client
        environment: GlobalConfig = self.get_environment(environment_name)
        test_environment = environment.test
        production_environment = environment.prod
        if env_mode.lower() in ["development", "test"]:
            env = test_environment
        else:
            env = production_environment

        if sd_basic_auth:
            sd_api_client = GravitateSDAPI(
                base_url=env.sd.base_url,
                username=env.sd.username,
                password=env.sd.password,
            )
        else:
            sd_api_client = GravitateSDAPI(
                base_url=env.sd.base_url,
                client_id=env.sd.client_id,
                client_secret=env.sd.client_secret,
            )

        return ClientConstructor(
            rita=Client(
                config=env.rita,
                api_client=GravitateRitaAPI(
                    tenant=environment_name,
                    client_id=env.rita.client_id,
                    client_secret=env.rita.client_secret,
                )
            ),
            sd=Client(
                config=env.sd,
                api_client=sd_api_client
            ),
            pe=Client(
                config=env.pe,
                api_client=GravitatePEAPI(base_url=env.pe.base_url,
                                          username=env.pe.username,
                                          password=env.pe.password,
                                          )
            )

        )

    def get_secret(self, project_id_override: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve the entire secret from Cloud Secret Manager.

        Gets the complete configuration containing all client/customer environments.

        Args:
            project_id_override: Optional project ID to use instead of the default.

        Returns:
            Dictionary containing the complete secret data with all client configurations.

        Raises:
            ConfigDoesNotExistException: If the secret does not exist.
            GlobalConfigException: If there's an error retrieving the secret.
        """
        try:
            secret = CloudSecretsClient.get_file(path=self.file_name, file_name=self.file_name,
                                                 project_id=project_id_override)
            if not secret:
                raise ConfigDoesNotExistException(f"Config file '{self.file_name}' does not exist")
            data = secret.data
            return json.loads(data)
        except ConfigDoesNotExistException:
            logger.error(f"Config file '{self.file_name}' does not exist")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve secret {self.file_name}: {str(e)}")
            raise GlobalConfigException(f"Error retrieving secret: {str(e)}")

    def get_environment(self, environment_name: str, project_id_override: Optional[str] = None) -> GlobalConfig:
        """Retrieve configuration for a specific client/customer.

        Gets the configuration data for a single environment (client/customer).
        Environment names are case-insensitive and will be converted to lowercase.

        Args:
            environment_name: Name of the client/customer environment.
            project_id_override: Optional project ID to use instead of the default.

        Returns:
            GlobalConfig object containing the configuration for the specified environment.

        Raises:
            EnvironmentDoesNotExistException: If the environment does not exist.
            GlobalConfigException: If there's an error retrieving the secret.
        """
        environment_name = environment_name.lower()
        try:
            secret = self.get_secret(project_id_override)
            if environment_name not in secret:
                raise EnvironmentDoesNotExistException(f"Environment '{environment_name}' does not exist")
            return GlobalConfig.model_validate(secret[environment_name])
        except ConfigDoesNotExistException:
            raise
        except EnvironmentDoesNotExistException:
            logger.error(f"Environment '{environment_name}' does not exist")
            raise
        except Exception as e:
            logger.error(f"Error getting environment '{environment_name}': {str(e)}")
            raise GlobalConfigException(f"Error retrieving environment '{environment_name}': {str(e)}")

    def dict_has_attribute(self, dictionary: Dict, attribute_name: str) -> bool:
        """Check if a dictionary has a specific key.

        Performs a case-insensitive check by converting the attribute name to lowercase.

        Args:
            dictionary: The dictionary to check.
            attribute_name: The key name to look for.

        Returns:
            True if the key exists, False otherwise.
        """
        attribute_name = attribute_name.lower()
        return attribute_name in dictionary

    def create_new_config(self, config: Dict[str, Any], project_id_override: Optional[str] = None):
        """Create a completely new configuration, replacing the entire secret.

        Use with caution as this replaces all existing client configurations.

        Args:
            config: Complete configuration dictionary to store.
            project_id_override: Optional project ID to use instead of the default.

        Raises:
            GlobalConfigException: If there's an error uploading the configuration.
        """
        try:
            self._upload_config(config_data=config, project_id_override=project_id_override)
        except Exception as e:
            logger.error(f"Failed to create new config: {str(e)}")
            raise GlobalConfigException(f"Failed to create new config: {str(e)}")

    def create_new_environment(self, environment_name: str, config: GlobalConfig,
                               project_id_override: Optional[str] = None) -> None:
        """Create a new configuration for a client/customer.

        Adds a new client-specific configuration to the existing secret.
        Environment names are case-insensitive and will be converted to lowercase.

        Args:
            environment_name: Name of the client/customer environment.
            config: Configuration object to store.
            project_id_override: Optional project ID to use instead of the default.

        Raises:
            EnvironmentAlreadyExistsException: If an environment with the given name already exists.
            GlobalConfigException: For any other errors during creation.
        """
        environment_name = environment_name.lower()
        try:
            secret_dict = self.get_secret(project_id_override=project_id_override)
            if self.dict_has_attribute(secret_dict, environment_name):
                raise EnvironmentAlreadyExistsException(f"Environment '{environment_name}' already exists")
            secret_dict[environment_name] = config.model_dump()
            self._upload_config(secret_dict)
        except EnvironmentAlreadyExistsException:
            logger.error(f"Environment '{environment_name}' already exists")
            raise
        except ConfigDoesNotExistException:
            # If the config doesn't exist yet, create a new one with just this environment
            try:
                new_config = {environment_name: config.model_dump()}
                self._upload_config(new_config, project_id_override)
            except Exception as e:
                logger.error(f"Failed to create new environment '{environment_name}': {str(e)}")
                raise GlobalConfigException(f"Failed to create new environment '{environment_name}': {str(e)}")
        except Exception as e:
            logger.error(f"Failed to create new environment '{environment_name}': {str(e)}")
            raise GlobalConfigException(f"Failed to create new environment '{environment_name}': {str(e)}")

    def overwrite_config(self, environment_name: str, config: GlobalConfig,
                         project_id_override: Optional[str] = None) -> None:
        """Overwrite an existing client/customer configuration.

        Updates the configuration for an existing environment.
        Environment names are case-insensitive and will be converted to lowercase.

        Args:
            environment_name: Name of the client/customer environment to update.
            config: New configuration object.
            project_id_override: Optional project ID to use instead of the default.

        Raises:
            EnvironmentDoesNotExistException: If the specified environment doesn't exist.
            GlobalConfigException: For any other errors during update.
        """
        environment_name = environment_name.lower()
        try:
            secret_dict = self.get_secret(project_id_override=project_id_override)
            if not self.dict_has_attribute(secret_dict, environment_name):
                raise EnvironmentDoesNotExistException(f"Environment '{environment_name}' does not exist")
            secret_dict[environment_name] = config.model_dump()
            self._upload_config(secret_dict)
        except EnvironmentDoesNotExistException:
            logger.error(f"Environment '{environment_name}' does not exist")
            raise
        except Exception as e:
            logger.error(f"Failed to overwrite environment '{environment_name}': {str(e)}")
            raise GlobalConfigException(f"Failed to overwrite environment '{environment_name}': {str(e)}")

    def delete_config(self, environment_name: str, project_id_override: Optional[str] = None) -> None:
        """Delete a configuration for a client/customer.

        Removes a client-specific configuration from the secret.
        Environment names are case-insensitive and will be converted to lowercase.

        Args:
            environment_name: Name of the client/customer environment to delete.
            project_id_override: Optional project ID to use instead of the default.

        Raises:
            EnvironmentDoesNotExistException: If the specified environment doesn't exist.
            GlobalConfigException: For any other errors during deletion.
        """
        environment_name = environment_name.lower()
        try:
            secret_dict = self.get_secret(project_id_override=project_id_override)
            if not self.dict_has_attribute(secret_dict, environment_name):
                raise EnvironmentDoesNotExistException(f"Environment '{environment_name}' does not exist")
            del secret_dict[environment_name]
            self._upload_config(secret_dict)
        except EnvironmentDoesNotExistException:
            logger.error(f"Environment '{environment_name}' does not exist")
            raise
        except Exception as e:
            logger.error(f"Failed to delete environment '{environment_name}': {str(e)}")
            raise GlobalConfigException(f"Failed to delete environment '{environment_name}': {str(e)}")

    def _upload_config(self, config_data: Dict[str, Any], project_id_override: Optional[str] = None) -> None:
        """Helper method to upload configuration to Cloud Secret Manager.

        Handles the serialization and upload of configuration data to the secret.
        Keep in mind that Google Cloud Secret Manager has a 64 KiB size limitation.

        Args:
            config_data: Configuration data to upload.
            project_id_override: Optional project ID to use instead of the default.

        Raises:
            GlobalConfigException: If there's an error uploading the configuration.
        """
        try:
            file = File(file_name=self.file_name, file_data=config_data, project_id=project_id_override)
            CloudSecretsClient.upload_file(path="", file=file)
            logger.info(f"Successfully updated configuration '{self.file_name}'")
        except Exception as e:
            logger.error(f"Failed to upload configuration '{self.file_name}': {str(e)}")
            raise GlobalConfigException(f"Failed to upload configuration: {str(e)}")


if __name__ == "__main__":
    gg = GlobalConfigManager()
    dd = gg.environment_from_name("Loves", "test")
    print(dd)
    config = GlobalConfig(
        prod=Configs(
            rita=Config(
                client_id=None,
                client_secret=None,
                psk=None,
                username=None,
                password=None,
                base_url=None,
            ),
            sd=Config(
                client_id=None,
                client_secret=None,
                psk=None,
                username=None,
                password=None,
                base_url=None,
            ),
            pe=Config(
                client_id=None,
                client_secret=None,
                psk=None,
                username=None,
                password=None,
                base_url=None,
            )
        ),
        test=Configs(
            rita=Config(
                client_id=None,
                client_secret=None,
                psk=None,
                username=None,
                password=None,
                base_url=None,
            ),
            sd=Config(
                client_id=None,
                client_secret=None,
                psk=None,
                username=None,
                password=None,
                base_url=None,
            ),
            pe=Config(
                client_id=None,
                client_secret=None,
                psk=None,
                username=None,
                password=None,
                base_url=None,
            )
        ),
        extra_data={
            "name": "loves"
        }
    )
    # gg.create_new_environment(environment_name="loves", config=config)
