from typing import Iterable, Callable

from bb_integrations_lib.provider.ftp.interface import FTPClient, SFTPClient, FTPClientInterface
from bb_integrations_lib.provider.ftp.model import FTPFileInfo, FTPType
from bb_integrations_lib.secrets.credential_models import FTPCredential
from bb_integrations_lib.shared.model import RawData, File
from bb_integrations_lib.util.utils import load_credentials


class FTPIntegrationClient:
    """
    A client for interacting with an FTP or SFTP server, offering methods for listing, uploading, downloading,
    renaming, and deleting files.
    Gracefully manages the FTP connection for you, handling timeouts and retries.

    Note that most commands are simply sent to the server, not double-checked - for example, a delete may not report an
    error even if the file doesn't exist.
    """

    def __init__(self, credentials: FTPCredential):
        self.credentials = credentials
        self.interface: FTPClientInterface
        match self.credentials.ftp_type:
            case FTPType.ftp:
                self.interface = FTPClient(self.credentials)
            case FTPType.ftps:
                self.interface = FTPClient(self.credentials)
            case FTPType.sftp:
                self.interface = SFTPClient(self.credentials)
            case FTPType.ftpes:
                self.interface = FTPClient(self.credentials)
            case _:
                raise Exception(f"Unknown FTP credential type {self.credentials.ftp_type}, please implement an adapter")
        self.cur_dir = "/"

    def __enter__(self):
        self.interface.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.interface.disconnect()

    def list_files(self, directory: str) -> Iterable[str]:
        """
        List all files in the given directory.
        :returns: An iterable of file names in the directory.
        """
        return self.interface.list_files(directory)

    def rename_file(self, old_name: str, new_name: str) -> None:
        """
        Rename a single file.
        :param old_name: The current name of the file.
        :param new_name: The name to change to.
        """
        return self.rename_files([(old_name, new_name)])

    def rename_files(self, files: Iterable[tuple[str, str]]) -> None:
        """
        Rename a batch of files.
        :param files: An iterable of tuples, each containing the old/new names for each files like (old, new).
        """
        return self.interface.rename_files(files)

    def delete_file(self, path: str) -> None:
        """
        Delete a single file.
        :param path: The path to the file to delete.
        """
        return self.delete_files([path])

    def delete_files(self, paths: Iterable[str]) -> None:
        """
        Delete a batch of files.
        :param paths: The paths to files to delete.
        """
        return self.interface.delete_files(paths)

    def upload_file(self, file: File, path: str) -> None:
        """
        Upload a single File to a given parent directory.
        :param file: The file to upload. Needs at least ``file_name`` and data of a type that ``file.to_bytes()``
          supports.
        :param path: The parent directory to upload the file to.
        """
        self.upload_files([file], path)

    def upload_files(self, files: Iterable[File], path: str) -> None:
        """
        Like ``upload_file``, but for a batch of files.
        :param files: An iterable of File objects to upload. See docs on ``upload_file`` for how these are handled.
        :param path: The parent directory to upload the files to.
        """
        self.interface.upload_files(files, path)

    def download_file(self, path: str) -> RawData:
        """
        Download a single file into memory.
        :param path: The remote path of the file to download.
        :return: A RawData object representing the downloaded file. ``file_name`` and ``data`` attributes will be set.
          ``data`` will be a BytesIO object pre-seeked to 0.
        :raises FileNotFoundError: If the file doesn't exist.
        """
        try:
            return next(iter(self.download_files([path])))
        except StopIteration:
            raise FileNotFoundError(f"Remote file {path} not found")

    def download_files(self, paths: Iterable[str]) -> Iterable[RawData]:
        """
        Like ``download_file``, but for a batch of files. Not all downloads may succeed; if any fail they will not be
        present in the result list. If none succeed, an empty list will be returned.
        :param paths: The remote paths of the files to download.
        :return:
        """
        return self.interface.download_files(paths)

    def get_file_info(self, path: str) -> FTPFileInfo:
        """
        Get details about a single file.
        :param path: The remote path of the file to get info for.
        :return: A FTPFileInfo object with details about the file. If this is an FTP connection, only the ``size``
          attribute is guaranteed. If this is an SFTP connection, all attributes but the permissions are guaranteed.
        """
        return self.interface.get_file_info(path)

    def download_dir(self, directory: str, filt: Callable[[str], bool] = None) -> Iterable[RawData]:
        """
        Download files from an entire directory, optionally filtering with the ``filt`` callable.

        :param directory: The directory to download.
        :param filt: An optional filter callable. Should take one argument (the file name) and return a boolean
          indicating whether to include the file..

        :returns: An iterable of `RawData` objects representing the downloaded files.
        """
        file_list = self.list_files(directory)
        if filt:
            file_list = filter(filt, file_list)
        return self.download_files(map(lambda file_name: f"{directory}/{file_name}", file_list))
