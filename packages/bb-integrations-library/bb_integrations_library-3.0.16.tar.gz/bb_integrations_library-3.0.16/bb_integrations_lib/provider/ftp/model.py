from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class FTPType(str, Enum):
    """
    Enumeration of supported FTP types.

    Attributes:
        ftps (str): FTPS (FTP over SSL) protocol.
        sftp (str): SFTP (SSH File Transfer Protocol) protocol.
        ftp (str): Standard FTP protocol.
        ftpes (str): FTPeS (FTP over explicit SSL) protocol.
    """
    ftps = "ftps"
    sftp = "sftp"
    ftp = "ftp"
    ftpes = "ftpes"


class FTPAuthType(str, Enum):
    """
    Enumeration of FTP authentication methods.

    Attributes:
        basic (str): Basic authentication with username and password.
        rsa (str): RSA authentication using private key.
    """
    basic = "basic"
    rsa = "rsa"


class FTPFileInfo(BaseModel):
    """
    Model representing metadata information about a file on the FTP server.

    Attributes:
        size (Optional[int]): Size of the file in bytes.
        permissions (Optional[str]): File permissions.
        owner_id (Optional[int]): User ID of the file owner.
        group_id (Optional[int]): Group ID of the file owner.
        last_access_time (Optional[int]): Timestamp of the last file access.
        last_modification_time (Optional[int]): Timestamp of the last file modification.
    """
    size: Optional[int] = None
    permissions: Optional[str] = None
    owner_id: Optional[int] = None
    group_id: Optional[int] = None
    last_access_time: Optional[int] = None
    last_modification_time: Optional[int] = None

    @property
    def last_modified_on(self):
        """
        Get the last modification date as a `datetime` object, if available.

        Returns:
            datetime or None: Last modified date if `last_modification_time` is set, otherwise None.
        """
        if self.last_modification_time:
            return datetime.fromtimestamp(self.last_modification_time)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert file info to a dictionary, including the `last_modified_on` property.

        Returns:
            Dict[str, Any]: Dictionary of file metadata with added `last_modified_on` field.
        """
        return {
            **self.model_dump(),
            "last_modified_on": self.last_modified_on,
        }

