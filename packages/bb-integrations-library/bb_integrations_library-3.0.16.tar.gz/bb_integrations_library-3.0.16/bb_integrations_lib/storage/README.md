# File Storage

A standard internal library to interact with file storage systems across integration processes.

# Installation

To install run:

- `pip install git+https://github.com/gravitate-energy/bb_file_storage.git`

# Requirements

- run `setup.py` to create default service_accounts files:
    - `ftp.credentials.json` for FTP, which must include:
        - `host`: `str`
        - `username`: `str`
        - `password`: `str`
        - `port`: `int` = 22
        - `ftp_type`: `str`
    - `aws.credentials.json` for AWS, must include:
        - `bucket_name`: `str`
        - `access_key_id`: `str`
        - `secret_access_key`: `str`
    - `google.credentials.json` for Google, must include:
        - `type`: `str`
        - `project_id`: `str`
        - `private_key_id`: `str`
        - `private_key`: `str`
        - `client_email`: `str`
        - `client_id`: `str`
        - `auth_uri`: `str`
        - `token_uri`: `str`
        - `auth_provider_x509_cert_url`: `str`
        - `client_x509_cert_url`: `str`
        - `universe_domain`: `str`

# Methods

Integrations within the library will follow the same protocol:

```python
class Integration(Protocol):
    def list_files(self, directory: str, credential_file_name: str = None) -> list[str]:
        """Integration method to list files in a remote directory"""
        pass

    def get_raw_data(self, min_date: datetime, credential_file_name: str = None, check_date: bool = True) -> \
            Iterable[RawData]:
        """Integration method to download a file from a remote directory"""
        pass

    def rename_file(self, old_name: str, new_name: str, credential_file_name: str = None) -> None:
        """Integration method to rename a remote file"""
        pass

    def delete_file(self, path: str, credential_file_name: str = None) -> None:
        """Integration method to delete a remote file"""
        pass

    def upload_file(self, file: File, path: str, credential_file_name: str = None) -> None:
        """Integration method to upload a file to a remote directory"""
        pass



```

### *Raw Data:

RawData is defined as follows:

```python
class RawData(BaseModel):
    file_name: str
    data: Any 
```

File is defined as follows:
```python
class File(BaseModel):
    file_name: str | None = None
    file_data: str
    content_type: str = 'text/csv'
    is_public: bool = False
    file_extension: str = 'csv'
    check_if_exists: bool = True
```

# Services

### FTP - SFTP

Support for both `FTP` and `SFTP` protocols.

- `ftp_type` will determine which protocol to use

*Examples:*

- Import FTP Client:

```python
from storage.ftp.client import FTPClient
```

- List files:

``` python
ls = FTPClient.list_files(directory="/")
```

- Rename file:

``` python
FTPClient.rename_file(old_name="old_folder/old_name.csv", new_name="new_folder/new_name.csv")
```

- Upload file:

``` python
 df = pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': ['a', 'b', 'c']
    })
    f = File(
        file_name="TestFile",
        file_data=df,
    )
 FTPClient.upload_file(file=f, path='Inbound')
```

- Get file:

``` python
FTPClient.get_file( path='folder/sub_folder', file_name='file_name.txt')
```

- Delete file:

``` python
FTPClient.delete_file( path='folder/file_name.txt')
```

### GCP - Cloud Storage

Support for Google Cloud Storage.

*Examples:*

- Import Google Client:

```python
from storage.gcs.client import GCSClient
```

- List files:

``` python
ls = GCSClient.list_files(directory="erp-export-bkp/japan")
```

- Rename file:

``` python
GCSClient().rename_file(old_name='bboil-integration-bkp/test/testfile.csv', new_name='bboil-integration-bkp/archive/testfile.csv')
```

- Upload file:

```python
df = pd.DataFrame({
    'column1': [1, 2, 3],
    'column2': ['a', 'b', 'c']
})
f = File(
    file_name="TestFile",
    file_data=df.to_csv(index=False),
)
GCSClient.upload_file(file=f, path="bboil-integration-bkp/test")
```

- Get file:

``` python
ff = GCSClient().get_file(path='bboil-integration-bkp/test/TestingSomeStuff', file_name="Test")
```

- Delete file:

``` python
GCSClient().delete_file(path='bboil-integration-bkp/archive/testfile.csv')
```

### GCP - Secret Manager
Support for Google Cloud Secret Manager.

*Examples:*

- Import Google Client:

```python
from storage.gcsmanager.client import GCSMClient
```

- List files:

``` python
ls = GCSMClient.list_files(directory="projects")
```

- Rename file:
Not Implemented

- Upload file:

```python
file_data = {'name': 'your-name'}
file = File(file_name="test", file_data=file_data)
GCSMClient.upload_file(file=file, path="/")
```

- Get file:

``` python

```

- Delete file:

``` python

```

### AWS - S3



