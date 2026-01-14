import warnings

from bb_integrations_lib.provider.aws.s3.client import S3Client

class AWSIntegration(S3Client):
    def __init__(self, *args, **kwargs):
        warnings.warn("Use provider.aws.s3.client.S3Client", DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)
