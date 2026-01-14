import ftplib
from abc import ABC
from io import BytesIO, StringIO
from pathlib import Path
from stat import S_ISREG
from typing import Iterable

import paramiko
import tenacity
from loguru import logger
from paramiko import RSAKey
from tenacity import retry_if_exception_type, stop_after_attempt, wait_fixed

from bb_integrations_lib.provider.ftp.model import FTPFileInfo, FTPAuthType, FTPType
from bb_integrations_lib.secrets.credential_models import FTPCredential
from bb_integrations_lib.shared.model import RawData, File


class FTPClientInterface(ABC):
    def __init__(self, credentials: FTPCredential):
        self.credentials = credentials
        self.first_connection = True

    def connect(self):
        self.first_connection = False

    def disconnect(self):
        raise NotImplementedError()

    def _reconnect(self, retry_state: tenacity.RetryCallState):
        raise NotImplementedError()

    def cwd(self, directory: str) -> None:
        raise NotImplementedError()

    def list_files(self, directory: str) -> Iterable[str]:
        raise NotImplementedError()

    def rename_files(self, files: Iterable[tuple[str, str]]) -> None:
        raise NotImplementedError()

    def delete_files(self, paths: Iterable[str]) -> None:
        raise NotImplementedError()

    def upload_files(self, files: Iterable[File], path: str) -> None:
        raise NotImplementedError()

    def download_files(self, paths: Iterable[str]) -> Iterable[RawData]:
        raise NotImplementedError()

    @staticmethod
    def reconnect_retry(func):
        def wrap(*args, **kwargs):
            if args[0].first_connection:
                args[0].connect()
            r = tenacity.Retrying(
                reraise=True,
                retry=retry_if_exception_type((OSError, AttributeError)),
                stop=stop_after_attempt(3),
                wait=wait_fixed(3),
                after=args[0]._reconnect
            )
            for attempt in r:
                with attempt:
                    return func(*args, **kwargs)

        return wrap

class FTPClient(FTPClientInterface):
    def __init__(self, credentials: FTPCredential):
        super().__init__(credentials)

        if self.credentials.ftp_type not in [FTPType.ftp, FTPType.ftps, FTPType.ftpes]:
            raise NotImplementedError(
                f"Attempted to use FTPClient with unsupported FTP type: {self.credentials.ftp_type} "
                "(only supports ftp, ftps, ftpes)"
            )

        self.is_tls = self.credentials.ftp_type in [FTPType.ftps, FTPType.ftpes]
        self.client: ftplib.FTP | None = None

    def connect(self):
        if self.is_tls:
            self.client = ftplib.FTP_TLS(
                host=self.credentials.host,
                user=self.credentials.username,
                passwd=self.credentials.password,
            )
            if self.credentials.ftp_type == FTPType.ftpes:
                self.client.prot_p()
        else:
            self.client = ftplib.FTP(
                host=self.credentials.host,
                user=self.credentials.username,
                passwd=self.credentials.password
            )
        super().connect()

    def disconnect(self):
        self.client.quit()
        # Will force a reconnection next time it is used
        self.first_connection = True

    def _reconnect(self, retry_state: tenacity.RetryCallState):
        # Targeted by reconnect_retry
        self.connect()

    @FTPClientInterface.reconnect_retry
    def list_files(self, directory: str) -> Iterable[str]:
        # Paths might be absolute - for consistency with the SFTP client, make them relative.
        return [Path(x).name for x in self.client.nlst(directory)]

    @FTPClientInterface.reconnect_retry
    def rename_files(self, files: Iterable[tuple[str, str]]) -> None:
        for old_name, new_name in files:
            logger.debug(f"Renaming file {old_name} -> {new_name}")
            self.client.rename(old_name, new_name)

    @FTPClientInterface.reconnect_retry
    def delete_files(self, paths: Iterable[str]) -> None:
        for path in paths:
            logger.debug(f"Deleting file {path}")
            self.client.delete(path)

    @FTPClientInterface.reconnect_retry
    def upload_files(self, files: Iterable[File], path: str) -> None:
        for file in files:
            name = file.file_name
            logger.debug(f"Uploading file {name}")
            self.client.storbinary(f"STOR {path}/{name}", File.to_bytes(file.file_data))


    @FTPClientInterface.reconnect_retry
    def download_files(self, paths: Iterable[str]) -> Iterable[RawData]:
        results = []
        for path in paths:
            logger.debug(f"Downloading {path}")
            buf = BytesIO()
            self.client.retrbinary(f"RETR {path}", buf.write)
            buf.seek(0)
            p = Path(path)
            results.append(RawData(file_name=p.name, data=buf))
        return results

    @FTPClientInterface.reconnect_retry
    def get_file_info(self, path: str) -> FTPFileInfo:
        # Size is guaranteed
        size = self.client.size(path)

        return FTPFileInfo(
            size=size,
            permissions=None,
            owner_id=None,
            group_id=None,
            last_access_time=None,
            last_modification_time=None,
        )


class SFTPClient(FTPClientInterface):
    def __init__(self, credentials: FTPCredential, private_key_path: str | None = None):
        super().__init__(credentials)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp: paramiko.SFTPClient | None = None
        self.private_key_path = private_key_path

    def connect(self):
        if self.credentials.private_key:
            pkey = RSAKey.from_private_key(
                StringIO(self.credentials.private_key),
                self.credentials.passphrase
            )
        elif self.credentials.auth_type == FTPAuthType.rsa:
            pkey = get_ppk()
        else:
            pkey = None


        self.ssh.connect(
            hostname=self.credentials.host,
            username=self.credentials.username,
            password=self.credentials.password,
            port=self.credentials.port or 22,
            key_filename=self.private_key_path,
            pkey=pkey,
            passphrase=self.credentials.passphrase,
            look_for_keys=False,
            allow_agent=False,
        )
        self.sftp = self.ssh.open_sftp()
        super().connect()

    def disconnect(self):
        self.sftp.close()
        self.first_connection = True

    def _reconnect(self, retry_state: tenacity.RetryCallState):
        self.connect()

    @FTPClientInterface.reconnect_retry
    def cwd(self, directory: str) -> None:
        self.sftp.chdir(directory)

    @FTPClientInterface.reconnect_retry
    def list_files(self, directory: str) -> Iterable[str]:
        logger.debug(f"Listing {directory}")
        res = self.sftp.listdir_attr(directory)
        return [x.filename for x in res if S_ISREG(x.st_mode)]


    @FTPClientInterface.reconnect_retry
    def rename_files(self, files: Iterable[tuple[str, str]]) -> None:
        for old_path, new_path in files:
            logger.debug(f"Renaming {old_path} -> {new_path}")
            return self.sftp.rename(old_path, new_path)

    @FTPClientInterface.reconnect_retry
    def delete_files(self, paths: Iterable[str]) -> None:
        for path in paths:
            logger.debug(f"Deleting {path}")
            self.sftp.remove(path)

    @FTPClientInterface.reconnect_retry
    def upload_files(self, files: Iterable[File], path: str) -> None:
        for file in files:
            name = file.file_name
            logger.debug(f"Uploading file {name}")
            self.sftp.putfo(file.to_bytes(file.file_data), f"{path}/{name}")

    @FTPClientInterface.reconnect_retry
    def download_files(self, paths: Iterable[str]) -> Iterable[RawData]:
        results = []
        for path in paths:
            logger.debug(f"Downloading {path}")
            buf = BytesIO()
            self.sftp.getfo(path, buf)
            buf.seek(0)
            p = Path(path)
            results.append(RawData(file_name=p.name, data=buf))
        return results

    @FTPClientInterface.reconnect_retry
    def get_file_info(self, path: str) -> FTPFileInfo:
        file_info = self.sftp.stat(path)
        return FTPFileInfo(
            size=file_info.st_size,
            permissions=oct(file_info.st_mode) if file_info.st_mode else None,
            owner_id=file_info.st_uid,
            group_id=file_info.st_gid,
            last_access_time=file_info.st_atime,
            last_modification_time=file_info.st_mtime,
        )

def get_ppk(path: str = 'secrets/id_rsa') -> RSAKey:
    """
        Given a path, try to load RSA key file
        :param path: The path to load
        :return: The loaded RSA key
    """
    try:
        private_key_path = Path(path)
        if not private_key_path.exists():
            raise FileNotFoundError(f"Private key file not found at: {private_key_path}")
        private_key: RSAKey = RSAKey.from_private_key_file(str(private_key_path))
        return private_key
    except FileNotFoundError as fne:
        msg = f'Failed to load private key from file: {path} -> {fne}'
        logger.error(msg)
        raise
    except Exception as e:
        msg = f'Failed to load private key from file: {path} -> {e}'
        logger.error(msg)
        raise