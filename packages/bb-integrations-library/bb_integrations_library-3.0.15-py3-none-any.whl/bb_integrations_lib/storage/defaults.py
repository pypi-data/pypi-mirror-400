from pydantic import BaseModel
from typing import Dict
from bb_integrations_lib.shared.model import CredentialType


class Default(BaseModel):
    name: str
    type: CredentialType
    credential: dict

    @property
    def file_name(self):
        return f'{self.type.value}.json'


class DefaultCredentials(BaseModel):
    credentials: Dict[str, Default]


# Example default objects
google_default = Default(
    name="Google",
    type=CredentialType.google,
    credential={
        "type": "",
        "project_id": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_x509_cert_url": "",
        "universe_domain": "googleapis.com"
    }
)

ftp_default = Default(
    name="FTP",
    type=CredentialType.ftp,
    credential={
        "username": "",
        "password": "",
        "host": "",
        "port": 0,
        "ftp_type": "sftp",
        "file_base_name": "",
        "base_dir": "",
        "date_format": "%Y-%m-%d-%H-%M"
    }
)

aws_default = Default(
    name="AWS",
    type=CredentialType.aws,
    credential={
        "bucket_name": "",
        "access_key_id": "",
        "secret_access_key": ""
    }
)

default_credentials = DefaultCredentials(credentials={
    "google": google_default,
    "ftp": ftp_default,
    "aws": aws_default
})

if __name__ == '__main__':
    for key, default in default_credentials.credentials.items():
        print(f"Key: {key}, File Name: {default.file_name}")
