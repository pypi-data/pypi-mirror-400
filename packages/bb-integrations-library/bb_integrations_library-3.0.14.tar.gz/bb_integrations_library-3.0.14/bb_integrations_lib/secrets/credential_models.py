from abc import ABC
from typing import Optional, Literal, Annotated, Union, Self

from pydantic import BaseModel, TypeAdapter, Field, field_validator

from bb_integrations_lib.provider.ftp.model import FTPAuthType, FTPType


class BadSecretException(Exception):
    pass


"""
A generic base class for any and all credentials. These must be storable in 1Password, so they need to be
tagged (set ``type_tag=cls.__name__``) so they can be discriminated from each other in a union (see ``AnyCredential``).
"""
class AbstractCredential(ABC, BaseModel):
    type_tag: str



class SDCredential(AbstractCredential):
    type_tag: Literal["SDCredential"] = "SDCredential"

    host: str
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    mongodb_conn_str: str | None = None


class PECredential(AbstractCredential):
    type_tag: Literal["PECredential"] = "PECredential"

    host: str
    username: str
    password: str
    client_id: str
    client_secret: str

class QTCredential(AbstractCredential):
    type_tag: Literal["QTCredential"] = "QTCredential"
    base_url: str
    qt_id: str
    carrier_id: str
    authorization: str


class RITACredential(AbstractCredential):
    type_tag: Literal["RITACredential"] = "RITACredential"

    base_url: str = "https://rita.gravitate.energy/api/"
    username: str | None = None
    password: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    tenant: str

class FTPCredential(AbstractCredential):
    """
    Model representing the credentials required to connect to an FTP server.

    Attributes:
        host (str): Host address of the FTP server.
        username (str): Username for FTP authentication.
        password (Optional[str]): Password for FTP authentication, if applicable.
        passphrase (Optional[str]): Passphrase for RSA authentication, if applicable.
        auth_type (Optional[FTPAuthType]): Type of authentication. Defaults to `FTPAuthType.basic`.
        port (int): Port number for FTP connection. Defaults to 22.
        ftp_type (FTPType): Type of FTP protocol.
        private_key (Optional[str]): Private key for RSA authentication, if applicable. Defaults to None.
    """
    type_tag: Literal["FTPCredential"] = "FTPCredential"

    host: str
    username: str
    password: Optional[str] = None
    passphrase: Optional[str] = None
    auth_type: Optional[FTPAuthType] = FTPAuthType.basic
    port: Optional[int] = None
    ftp_type: FTPType
    private_key: Optional[str] = None


class AWSCredential(AbstractCredential):
    """
    Model representing AWS credentials required for accessing an S3 bucket.

    Attributes:
        bucket_name (str): The name of the S3 bucket.
        access_key_id (str): AWS access key ID used for authentication.
        secret_access_key (str): AWS secret access key used for authentication.
    """
    type_tag: Literal["AWSCredential"] = "AWSCredential"

    bucket_name: str
    access_key_id: str
    secret_access_key: str


class GoogleCredential(AbstractCredential):
    """
    Model for Google Cloud credentials.

    Attributes:
        type (str): Credential type.
        project_id (str): Project ID.
        private_key_id (str): Private key ID.
        private_key (str): Private key string.
        client_email (str): Client email address.
        client_id (str): Client ID.
        auth_uri (str): Authentication URI.
        token_uri (str): Token URI.
        auth_provider_x509_cert_url (str): URL to the x509 certificate of the auth provider.
        client_x509_cert_url (str): URL to the x509 certificate of the client.
        universe_domain (str): Universe domain.
    """
    type_tag: Literal["GoogleCredential"] = "GoogleCredential"

    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str

    @field_validator("private_key", mode="after")
    @classmethod
    def unescape_newlines(cls, v):
        return v.replace("\\n", "\n")


# TODO: These are not compatible with the flat field layout that 1P secrets require
class IMAPAuthOAuth(BaseModel):
    """OAuth IMAP authentication flow."""
    client_id: str
    client_secret: str
    refresh_token: str


class IMAPAuthSimple(BaseModel):
    """Simple (password) IMAP authentication flow."""
    password: str


class IMAPCredential(AbstractCredential):
    """
    Model representing required to connect to an IMAP server and inbox.
    """
    type_tag: Literal["IMAPCredential"] = "IMAPCredential"

    host: str
    port: int
    email_address: str
    auth: IMAPAuthOAuth | IMAPAuthSimple


class MongoDBCredential(AbstractCredential):
    type_tag: Literal["MongoDBCredential"] = "MongoDBCredential"

    mongo_conn_str: str
    mongo_db_name: str

class PlatformScienceCredential(AbstractCredential):
    type_tag: Literal["PlatformScienceCredential"] = "PlatformScienceCredential"

    base_url: str
    client_id: str
    client_secret: str

class CargasCredential(AbstractCredential):
    type_tag: Literal["CargasCredential"] = "CargasCredential"

    base_url: str
    api_key: str

class KeyVuCredential(AbstractCredential):
    type_tag: Literal["KeyVuCredential"] = "KeyVuCredential"

    credential: str


"""Any credential that can be stored and retrieved in a secrets manager."""
AnyCredential = TypeAdapter(Annotated[Union[
    SDCredential,
    PECredential,
    QTCredential,
    RITACredential,
    FTPCredential,
    AWSCredential,
    GoogleCredential,
    IMAPCredential,
    MongoDBCredential,
    PlatformScienceCredential,
    CargasCredential,
    KeyVuCredential
], Field(discriminator="type_tag")])

allowed_onepassword_models: dict[str, AbstractCredential] = {
    k: v["cls"]
    for k, v in AnyCredential.core_schema["choices"].items()
}
onepassword_category_map = {
    SDCredential: "LOGIN",
    PECredential: "LOGIN",
    QTCredential: "API",
    RITACredential: "LOGIN",
    FTPCredential: "SERVER",
    AWSCredential: "API",
    GoogleCredential: "API",
    IMAPCredential: "EMAIL",
    MongoDBCredential: "DATABASE",
    PlatformScienceCredential: "API",
    CargasCredential: "API",
    KeyVuCredential: "API"
}
