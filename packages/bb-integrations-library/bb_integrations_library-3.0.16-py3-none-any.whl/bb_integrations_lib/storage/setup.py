"""
Script for initiating the package.
    - Creates [service].credentials.json if not in project
    - Tries to create secrets for storage services if not created
"""
import json
import os

from loguru import logger

from bb_integrations_lib.storage.defaults import default_credentials


def check_credentials() -> None:
    for key, default in default_credentials.credentials.items():
        if not os.path.exists(default.file_name):
            logger.debug(f'Could not find {default.file_name},creating {key} default credentials')
            with open(default.file_name, "w") as f:
                credentials_data = default_credentials.credentials[key].credential
                json.dump(credentials_data, f, indent=4)
    return None


def setup():
    check_credentials()


if __name__ == '__main__':
    setup()
