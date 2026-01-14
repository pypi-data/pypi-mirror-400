import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, AsyncIterator

from loguru import logger

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.protocols.pipelines import GeneratorStep
from bb_integrations_lib.provider.ftp.client import FTPIntegrationClient
from bb_integrations_lib.secrets.credential_models import FTPCredential
from bb_integrations_lib.provider.ftp.model import FTPType
from bb_integrations_lib.shared.model import RawData, FileConfigRawData, ConfigMode, ConfigMatchMode
from bb_integrations_lib.util.utils import check_if_file_greater_than_date, file_exact_match


class SFTPFileConfigStep(GeneratorStep):

    def __init__(self, rita_client: GravitateRitaAPI,
                 ftp_client: FTPIntegrationClient | dict[str, FTPIntegrationClient], mode: ConfigMode,
                 match_mode: ConfigMatchMode = ConfigMatchMode.Partial, bucket_name: str | None = None,
                 config_name: str | None = None, min_date: datetime = datetime.min, strip_trailing_digits:bool=False, *args,
                 **kwargs) -> None:
        """
        Imports SFTP files based on the provided or discovered fileconfigs.

        :param rita_client: The RITA client to use to retrieve fileconfigs.
        :param ftp_client: The FTP client, or a dict of FTP clients with keys matching confignames, to use to retrieve
          data.
        :param mode: How the step should discover fileconfigs.
        :param match_mode: How the step should match fileconfigs to various properties of the files being scanned.
        :param bucket_name: The bucket name which holds fileconfigs, for FromBucket and ByName modes.
        :param config_name: The fileconfig name, if using ByName mode.
        :param min_date: Filter out files with a date before this.
        """
        super().__init__(*args, **kwargs)
        self.rita_client = rita_client
        self.ftp_client = ftp_client
        self.mode = mode

        self.match_mode = match_mode
        self.strip_trailing_digits = strip_trailing_digits
        self.bucket_name = bucket_name
        self.config_name = config_name
        self.min_date = min_date
        self.file_configs: dict[str, Any] = {}

        if self.mode == ConfigMode.FromBucket and not self.bucket_name:
            raise ValueError("Cannot use FromBucket mode without setting a bucket_name")
        if self.mode == ConfigMode.ByName and not self.bucket_name:
            raise ValueError("Cannot use ByName mode without setting a bucket_name")
        if self.mode == ConfigMode.ByName and not self.config_name:
            raise ValueError("Cannot use ByName mode without setting a config_name")

    async def load_file_configs(self):
        if self.mode == ConfigMode.AllFiltered:
            self.file_configs = await self.rita_client.get_file_configs()
        elif self.mode == ConfigMode.FromBucket:
            self.file_configs = await self.rita_client.get_fileconfigs_from_bucket(self.bucket_name)
        elif self.mode == ConfigMode.ByName:
            self.file_configs = await self.rita_client.get_fileconfig_by_name(self.bucket_name, self.config_name)
        logger.info(f"Loaded {len(self.file_configs)} fileconfigs: {self.config_name}")

    def describe(self) -> str:
        return "Importing SFTP files based on file configs"

    async def generator(self, i: Any) -> AsyncIterator[RawData]:
        await self.load_file_configs()

        for config_name, file_config in self.file_configs.items():
            if isinstance(self.ftp_client, dict):
                selected_ftp_client = self.ftp_client[config_name]
            else:
                selected_ftp_client = self.ftp_client
            logger.info(f"Scanning with fileconfig '{config_name}' in directory {file_config.inbound_directory}")
            file_names = list(selected_ftp_client.list_files(file_config.inbound_directory))
            for idx, file_name in enumerate(file_names):
                if self.match_mode == ConfigMatchMode.Exact:
                    logger.info(f"Exact Matching file {file_name}")
                    if not file_exact_match(file_name, file_config.file_name):
                        logger.debug(f"Skipping file {file_name} due to not matching exactly to {file_config.file_name}")
                        continue
                elif self.match_mode == ConfigMatchMode.Partial:
                    if not file_config.file_name in file_name:
                        continue
                elif self.match_mode == ConfigMatchMode.ByExtension:
                    if not file_name.endswith(file_config.file_extension):
                        continue
                if file_config.date_format != "" and \
                    not check_if_file_greater_than_date(file_name, file_config.file_name, file_config.date_format,
                                                        self.min_date, self.strip_trailing_digits):
                    logger.debug(f"Skipping file {file_name} due to having date > {self.min_date}")
                    continue
                logger.info(f"fetching {idx+1}/{len(file_names)}: {file_name}")
                rd = selected_ftp_client.download_file(str(Path(file_config.inbound_directory) / Path(file_name)))
                self.pipeline_context.file_config = file_config
                yield FileConfigRawData(data=rd.data, file_name=rd.file_name, file_config=file_config)


if __name__ == "__main__":
    async def main():
        s = SFTPFileConfigStep(
            rita_client=GravitateRitaAPI(
                base_url="",
                username="",
                password=""
            ),
            ftp_client=FTPIntegrationClient(
                credentials=FTPCredential(
                    host="",
                    username="",
                    password="",
                    port=22,
                    ftp_type=FTPType.sftp
                ),
            ),
            mode=ConfigMode.ByName,
            config_name="my_config"
        )
        async for r in s.generator(None):
            print(r)

    asyncio.run(main())