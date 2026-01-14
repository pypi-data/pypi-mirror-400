import json
import pprint
from json import JSONDecodeError

import httpx
from async_lru import alru_cache
from httpx import HTTPStatusError
from requests import Response

from bb_integrations_lib.models.rita.bucket import Bucket
from bb_integrations_lib.models.rita.crossroads_mapping import CrossroadsMapping, CrossroadsMappingResult, \
    MappingRequest
from bb_integrations_lib.models.rita.crossroads_monitoring import CrossroadsMappingError, CrossroadsError
from bb_integrations_lib.models.rita.reference_data import ReferenceDataMapping
from typing import Optional, Dict, Union, List, runtime_checkable, Protocol, Self

import loguru
from pydantic import ValidationError, BaseModel

from bb_integrations_lib.gravitate.base_api import BaseAPI
from bb_integrations_lib.secrets import RITACredential
from bb_integrations_lib.util.utils import CustomJSONEncoder
from bb_integrations_lib.models.probe.resume_token import ResumeToken
from bb_integrations_lib.models.rita.audit import CreateReportV2, ProcessReportBaseV2, UpdateReportV2
from bb_integrations_lib.models.rita.config import FileConfig, Config, GenericConfig, ConfigType, MaxSync
from bb_integrations_lib.models.rita.email import EmailData
from bb_integrations_lib.models.rita.issue import IssueBase, UpdateIssue
from bb_integrations_lib.models.rita.mapping import Map
from bb_integrations_lib.models.rita.probe import ProbeConfig
from bb_integrations_lib.protocols.flat_file import TankReading

def catch_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            loguru.logger.error(f"HTTP status error: {e}")
            raise e
        except httpx.ConnectError as e:
            loguru.logger.error(f"Connection error: {e}")
            raise e
        except httpx.ReadTimeout as e:
            loguru.logger.error(f"Read timeout: {e}")
            raise e
        except Exception as e:
            loguru.logger.error(f"Unexpected error: {e}")
            raise e
    return wrapper

@runtime_checkable
class RitaBackendAPI(Protocol):
    async def get_mappings(self, source_system: Optional[str] = None, mapping_type: Optional[str] = None) -> list[Map]:
        """Gets all mappings by source_system and mapping type from RITA"""

    async def get_process_reports_sync(self, config_id: str) -> dict:
        """Gets latest sync date for a specific config"""

    async def get_file_configs(self, name: Optional[str] = None) -> dict[str, FileConfig]:
        """Gets File Configs from RITA"""

    async def create_process_report(self, new_process: CreateReportV2) -> ProcessReportBaseV2:
        """Creates a new process report in RITA"""

    async def get_config_by_id(self, id: str) -> Config:
        """Get a config by its id"""

    async def get_config_by_name(self, bucket_path: str, config_name: str) -> Dict[str, Union[FileConfig, ProbeConfig, GenericConfig]]:
        """Gets a config by its name"""

class GetMappings(BaseModel):
    source_system: Optional[str] = None


class GetConfigs(BaseModel):
    name: Optional[str] = None


class GravitateRitaAPI(BaseAPI):
    def __init__(
            self,
            client_id: str | None = None,
            client_secret: str | None = None,
            username: str | None = None,
            password: str | None = None,
            tenant: str | None = None,
            raise_errors: bool = True,
            base_url: str = "https://rita.gravitate.energy/api/"
    ):
        super().__init__(raise_errors)
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.tenant = tenant
        self._token = None

    async def _get_token(self):
        try:
            if self.username and self.password:
                resp = await self.post(
                    url=f"{self.base_url}auth/token",
                    data={"username": self.username, "password": self.password},
                )
            elif self.client_id and self.client_secret:
                resp = await self.post(
                    url=f"{self.base_url}auth/token",
                    data={"client_id": self.client_id, "client_secret": self.client_secret},
                )
            else:
                raise RuntimeError("Missing credentials for token request")
        except Exception:
            raise ValueError(f"Error Getting Token for {self.base_url}")

        try:
            self._token = resp.json()["access_token"]
            return self._token
        except Exception:
            raise ValueError(f"Could Not Get Token for {self.base_url} -> {resp.status_code}")

    async def _auth_req(self, method="POST", **kwargs):
        if not self._token:
            await self._get_token()

        headers = kwargs.pop("headers", {})
        headers["authorization"] = f"Bearer {self._token}"
        headers["X-Tenant-Name"] = self.tenant
        kwargs["headers"] = headers
        kwargs["url"] = f"{self.base_url}{kwargs.get("url", "")}"

        resp = await self.request(method, **kwargs)

        if resp.status_code == 401:
            await self._get_token()
            headers["authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers
            resp = await self.request(method, **kwargs)

        if resp.status_code == 422:
            try:
                resp_content = pprint.pformat(resp.json())
            except JSONDecodeError:
                resp_content = resp.text
            raise HTTPStatusError(
                f"Bad request: \n{resp_content}",
                request=resp.request,
                response=resp
            )

        return resp

    @classmethod
    def from_credential(cls, credential: RITACredential) -> Self:
        return cls(
            base_url=credential.base_url,
            username=credential.username,
            password=credential.password,
            client_id=credential.client_id,
            client_secret=credential.client_secret,
            tenant=credential.tenant,
        )

    async def token_post(self, **kwargs):
        return await self._auth_req("POST", **kwargs)

    async def token_get(self, **kwargs):
        return await self._auth_req("GET", **kwargs)

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_file_configs(self, name: Optional[str] = None) -> dict[str, FileConfig]:
        try:
            _data = (GetConfigs(name=name).model_dump() if name else {})
            resp = await self.token_post(url="config/all", json=_data)
            resp.raise_for_status()
            return self.build_fileconfig_dict(resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while fetching configurations: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_config_by_name(self, bucket_path: str, config_name: str) -> Dict[str, Union[FileConfig, ProbeConfig, Dict]]:
        try:
            data = {"bucket_path": bucket_path, "name": config_name,
                    "bucket_name": bucket_path}  # Some older versions of RITA use bucket_name instead of bucket_path
            resp = await self.token_post(url="config/by_name", json=data)
            resp.raise_for_status()
            return self.build_config_dict([resp.json()])
        except Exception as e:
            loguru.logger.error(f"Error while fetching configs from bucket: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_all_buckets(self) -> list[dict]:
        resp = await self.token_post(url="bucket/all")
        resp.raise_for_status()
        return resp.json()

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_mappings(self, source_system: Optional[str] = None, mapping_type: Optional[str] = None) -> list[Map]:
        try:
            _data = (GetMappings(source_system=source_system).model_dump() if source_system else {})
            resp = await self.token_post(url="integration/mappings/all", json=_data)
            resp.raise_for_status()
            mappings: List[Map] = [Map.model_validate(obj) for obj in resp.json()]
            if mapping_type:
                mappings = list(filter(lambda m: m.type == mapping_type, mappings))
            return mappings
        except Exception as e:
            loguru.logger.error(f"Error while fetching mappings: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        def is_valid(obj) -> bool:
            try:
                map = Map.model_validate(obj)
                return map.is_active
            except ValidationError:
                return False

        try:
            resp = await self.token_post(url="mapping/by_source_system/", params={"source_system": source_system})
            resp.raise_for_status()
            mappings = [Map.model_validate(obj) for obj in resp.json() if is_valid(obj)]
            return mappings
        except Exception as e:
            loguru.logger.error(f"Error while fetching mappings: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_process_reports_sync(self, config_id: str, status: str = None):
        try:
            data = {
                "config_id": config_id,
                "status": status
            }
            resp = await self.token_post(url="process_report/latest_sync", params=data)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            loguru.logger.error(f"Error while fetching process reports sync date: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_mappings_by_bucket_path(self, bucket_path: str) -> list[Map]:
        try:
            resp = await self.token_post(url="mapping/by_bucket_path", json=bucket_path)
            resp.raise_for_status()
            return [Map.model_validate(obj) for obj in resp.json()]
        except Exception as e:
            loguru.logger.error(f"Error while fetching mappings: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_fileconfigs_from_bucket(self, bucket_path: str) -> dict[str, FileConfig]:
        try:
            resp = await self.token_post(url="config/from_bucket", json=bucket_path)
            resp.raise_for_status()
            return self.build_fileconfig_dict(resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while fetching configs from bucket: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_config_by_id(self, id: str) -> Config:
        try:
            resp = await self.token_post(url=f"config/{id}")
            resp.raise_for_status()
            return Config.model_validate(resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while fetching config: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_fileconfig_by_name(self, bucket_path: str, config_name: str) -> dict[str, FileConfig]:
        try:
            data = {"bucket_path": bucket_path, "name": config_name,
                    "bucket_name": bucket_path}  # Some older versions of RITA use bucket_name instead of bucket_path
            resp = await self.token_post(url="config/by_name", json=data)
            resp.raise_for_status()
            return self.build_fileconfig_dict([resp.json()])
        except Exception as e:
            loguru.logger.error(f"Error while fetching configs from bucket: {e}")
            raise e

    @catch_exceptions
    @alru_cache(maxsize=128)
    async def get_probeconfig_by_name(self, bucket_path: str, config_name: str) -> dict[str, ProbeConfig]:
        try:
            data = {"bucket_path": bucket_path, "name": config_name}
            resp = await self.token_post(url="config/by_name", json=data)
            resp.raise_for_status()
            configs = [Config.model_validate(resp.json())]
            return self.build_probeconfig_dict(configs)
        except Exception as e:
            loguru.logger.error(f"Error while fetching config '{config_name}' from bucket '{bucket_path}': {e}")
            raise e

    @catch_exceptions
    async def get_config_max_sync(self, config_id: str) -> Response:
        try:
            resp = await self.token_post(url="config/max_sync", params={"config_id": config_id})
            resp.raise_for_status()
            return resp
        except Exception as e:
            loguru.logger.error(f"Error while fetching configurations: {e}")
            raise e

    @catch_exceptions
    async def update_config_max_sync(self, config_id: str, max_sync: MaxSync) -> Response:
        try:
            resp = await self.token_post(url="config/update_max_sync", params={"config_id": config_id}, json=max_sync.model_dump(mode="json"))
            resp.raise_for_status()
            return resp
        except Exception as e:
            loguru.logger.error(f"Error while fetching configurations: {e}")
            raise e


    @catch_exceptions
    async def get_resume_token(self, probe_id: str) -> ResumeToken | None:
        try:
            resp = await self.token_post(url=f"probe/get_resume_token/{probe_id}")
            resp.raise_for_status()
            resp = resp.json()
            if resp is not None:
                return ResumeToken.model_validate(resp)
            return None
        except Exception as e:
            loguru.logger.error(f"Error while fetching resume token: {e}")
            raise e

    @catch_exceptions
    async def get_available_tenants(self):
        try:
            resp = await self.token_post(url="/meta/tenant/available")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            loguru.logger.error(f"Error while fetching available tenants: {e}")
            raise e

    @catch_exceptions
    async def set_resume_token(self, resume_token: ResumeToken):
        try:
            resp = await self.token_post(url=f"probe/set_resume_token", json=resume_token.model_dump())
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            loguru.logger.error(f"Error while setting resume token: {e}, resp={resp} {resp.content()}")
            raise e

    async def get_estick_wr(self, store_number: str, tank_number: str) -> TankReading:
        try:
            resp = await self.token_post(url="estick/wr", params={"store_number": store_number, "tank_id": tank_number})
            resp.raise_for_status()
            return TankReading(**resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while fetching Warren Rogers estick reading: {e}")
            raise e

    async def get_estick_wr_many(self, store_number: str, tank_numbers: list[str]) -> list[TankReading]:
        try:
            resp = await self.token_post(url="estick/wr/many",
                                       json={"store_number": store_number, "tank_ids": tank_numbers})
            resp.raise_for_status()
            return [TankReading(**reading) for reading in resp.json()]
        except Exception as e:
            loguru.logger.error(f"Error while fetching multiple Warren Rogers estick readings: {e}")
            raise e

    @catch_exceptions
    async def create_process_report(self, new_process: CreateReportV2) -> ProcessReportBaseV2:
        try:
            _data = new_process.model_dump(exclude_none=True)
            payload_json = json.dumps(_data, cls=CustomJSONEncoder)
            # 30s timeout - large files may take a long time to upload
            resp = await self.token_post(url="process_report/create", json=json.loads(payload_json), timeout=30.0)
            resp.raise_for_status()
            return ProcessReportBaseV2(**resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while creating process_report: {e}")
            raise e

    async def update_process_report(self, update_process: UpdateReportV2) -> ProcessReportBaseV2:
        try:
            _data = update_process.model_dump(exclude_none=True)
            payload_json = json.dumps(_data, cls=CustomJSONEncoder)
            resp = await self.token_post(url="process_report/update", json=json.loads(payload_json))
            resp.raise_for_status()
            return ProcessReportBaseV2(**resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while creating process_report: {e}")
            raise e

    async def record_many_issues(self, issues: List[IssueBase]):
        try:
            res = await self.token_post(url="issue/record_many", json=[issue.model_dump(mode="json") for issue in issues])
            res.raise_for_status()
            # Endpoint does not return anything other than the status code
        except Exception as e:
            loguru.logger.error(f"Error while recording issue(s): {e}")
            raise e

    async def record_issue(self, issue: IssueBase):
        await self.record_many_issues([issue])

    async def update_issue(self, issue: UpdateIssue) -> IssueBase:
        try:
            resp = await self.token_post(url="issue/update", content=issue.model_dump_json(exclude_unset=True))
            resp.raise_for_status()
            return IssueBase(**resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while updating issue {issue.key}: {e}")
            raise e

    async def get_issue(self, key: str) -> IssueBase:
        try:
            resp = await self.token_post(url=f"issue/get/{key}")
            resp.raise_for_status()
            return IssueBase(**resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while updating issue {key}: {e}")
            raise e

    async def get_issues_by_config_id(self, config_id: str) -> list[IssueBase]:
        try:
            resp = await self.token_post(url=f"issue/by_config_id/{config_id}")
            resp.raise_for_status()
            content = resp.json()
            return [IssueBase(**item) for item in content]
        except Exception as e:
            loguru.logger.error(f"Error while fetching issues by config id {config_id}: {e}")
            raise e

    async def call_ep(self, url: str, params: dict = None, json: dict = None, method: str = "POST") -> Response:
        if method == "POST":
            return await self.token_post(url=url, params=params, json=json)
        if json is not None:
            raise ValueError("JSON is not supported for GET requests")
        return await self.token_get(url=url, params=params)

    async def update_config_value(self, config_id: str, new_value: dict):
        try:
            config = await self.get_config_by_id(config_id)
            config.config = new_value
            update_req = json.loads(config.model_dump_json())
            update_req["_id"] = config_id
            resp = await self.token_post(url=f"config/update", json=update_req)
            resp.raise_for_status()
            return Config.model_validate(resp.json())
        except Exception as e:
            loguru.logger.error(f"Error while updating config {config_id}: {e}")
            raise e

    @catch_exceptions
    async def send_email(self, email: EmailData, timeout: float = 10.0) -> Response:
        """Sends an email via RITA. Default timeout is 10 seconds. Large emails may take longer to send."""
        return await self.token_post(url="integration/send_email", json=email.model_dump(), timeout=timeout)

    @alru_cache(maxsize=64)
    async def get_connection(self, connection_id: str) -> dict:
        return await self.token_get(url=f"crossroads/network/connections/{connection_id}")

    async def get_crossroads_mapping(self, req: MappingRequest) -> MappingRequest:
        try:
            resp = await self.token_post(url=f"crossroads_2/map", json=req.model_dump(mode="json"))
            if resp.status_code == 499:
                # There was an error while mapping. Parse the detail and re-raise the error.
                js = resp.json()["detail"]
                raise CrossroadsMappingError(**js)
            if resp.status_code == 500:
                raise ValueError(resp.content)
            content = resp.json()
            result = MappingRequest.model_validate(content)
            return result
        except Exception as e:
            loguru.logger.error(f"Unexpected error while fetching Crossroads mapping: {e}")
            raise e



    def build_single_fileconfig_dict(self, config: Config) -> FileConfig:
        """
        Converts a config to  File Config.
        """
        file_config = FileConfig.model_validate(config.config)
        file_config.config_id = config.id  # Add the config's ID to the fileconfig obj, in case it's needed later.
        return file_config

    def build_single_probeconfig_dict(self, config: Config) -> ProbeConfig:
        """
        converts a config into a ProbeConfig.
        """
        return ProbeConfig.model_validate(config.config)


    def build_config_dict(self, configs: List[Dict]) -> Dict[str, Union[FileConfig, ProbeConfig, GenericConfig]]:
        """Builds a config lkp by name and parses each config to its respective model"""
        output = {}
        for c in configs:
            config = Config.model_validate(c)
            if config.type == ConfigType.fileconfig:
                output[config.name] = self.build_single_fileconfig_dict(config)
            elif config.type == ConfigType.probeconfig:
                output[config.name] = self.build_single_probeconfig_dict(config)
            else:
                output[config.name] = GenericConfig(config_id=  c.get("_id"), config = config.config)
        return output

    def build_probeconfig_dict(self, configs: List[Config]) -> Dict[str, ProbeConfig]:
        """
        Converts a list of configs of any type into a dict mapping config name to parsed ProbeConfig. Skips entries
        that are not ProbeConfigs, so the output dict may be smaller than the input list.
        """
        probe_configs = [c for c in configs if c.type == ConfigType.probeconfig]
        output = {}
        for config in probe_configs:
            parsed_probe_config = ProbeConfig.model_validate(config.config)
            output[config.name] = parsed_probe_config
        return output

    def build_fileconfig_dict(self, configs: list[dict]) -> dict[str, FileConfig]:
        """
        Converts a list of configs of any type into a dict mapping config name to parsed FileConfig. Skips entries
        that are not FileConfigs, so the output dict may be smaller than the input list.
        """
        output = {}
        for c in configs:
            config = Config.model_validate(c)
            if config.type == ConfigType.fileconfig:
                file_config = FileConfig.model_validate(config.config)
                file_config.config_id = c.get("_id")  # Add the config's ID to the fileconfig obj, in case it's needed later.
                output[config.name] = file_config
        return output
