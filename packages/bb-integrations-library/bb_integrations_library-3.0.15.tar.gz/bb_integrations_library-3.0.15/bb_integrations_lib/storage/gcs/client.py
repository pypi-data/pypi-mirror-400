import warnings

from bb_integrations_lib.provider.gcp.cloud_storage.client import CloudStorageClient

class GCSClient(CloudStorageClient):
    def __init__(self):
        warnings.warn("Use provider.gcp.cloud_storage.client.CloudStorageClient", DeprecationWarning, stacklevel=2)
        super().__init__()
