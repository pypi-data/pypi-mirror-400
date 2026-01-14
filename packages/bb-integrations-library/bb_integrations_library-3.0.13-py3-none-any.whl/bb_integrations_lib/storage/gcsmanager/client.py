import warnings

from bb_integrations_lib.provider.gcp.cloud_secrets.client import CloudSecretsClient

class GCSMClient(CloudSecretsClient):
    def __init__(self):
        warnings.warn("Use provider.gcp.cloud_secrets.client.CloudSecretsClient", DeprecationWarning, stacklevel=2)
        super().__init__()
