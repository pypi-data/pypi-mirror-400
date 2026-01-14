from typing import Protocol, Optional, Dict, Any
from pymongo.database import Database


class System(Protocol):
    sd: str
    pe: str
    rita: str


class GravitateConfig(Protocol):
    system_psk: Optional[str]
    url: Optional[str]
    conn_str: Optional[str]
    dbs: Optional[Dict[str, str]]
    system: Optional[System]
    short_name: Optional[str]
    admin_username: Optional[str]
    admin_password: Optional[str]


class SecureWebAPI(Protocol):
    system_name: str
    username: Optional[str]
    password: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    psk: str
    base_url: str
    token: Optional[str]
    system: Any
    extra_headers: Dict[str, str]

    def post(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None,
             data: Optional[Dict] = None, json: Optional[Dict] = None, files: Optional[Dict] = None,
             timeout: int = 180, raise_error: bool = True) -> Any: ...

    def get(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None,
            timeout: int = 180, raise_error: bool = True) -> Any: ...

    def token_post(self, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None,
                   json: Optional[Dict] = None, files: Optional[Dict] = None, timeout: int = 180,
                   raise_error: bool = True, headers: Optional[Dict] = None) -> Any: ...

    def token_get(self, url: str, params: Optional[Dict] = None, timeout: int = 180,
                  raise_error: bool = True) -> Any: ...

    def psk_post(self, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None,
                 json: Optional[Dict] = None, timeout: int = 180, psk_param: str = "system_psk",
                 raise_error: bool = True) -> Any: ...

    def get_service_api(self, service_name: str) -> 'SecureWebAPI': ...


class DatabaseAPI(Protocol):
    dbs: Dict[str, str]
    conn_string: str
    client: Any
    backend: Optional[Database]
    price: Optional[Database]
    payroll: Optional[Database]
    auth: Optional[Database]
    forecast: Optional[Database]
    ims: Optional[Database]
    valuation: Optional[Database]

    def get_db(self, db_name: str) -> Optional[Database]: ...


class WebAPIWrapper(Protocol):
    pass


class GravitateAPIClient(Protocol):
    system: System
    web: SecureWebAPI
    db: DatabaseAPI
    client_id: Optional[str]
    client_secret: Optional[str]
    base_url: str
    url: str
    system_name: Optional[str]
    short_name: Optional[str]
    username: Optional[str]
    password: Optional[str]
    psk: Optional[str]
    connection_string: Optional[str]
    dbs: Optional[Dict[str, str]]
    api_map: Dict[Any, WebAPIWrapper]
    apis: WebAPIWrapper


class SDWebAPIWrapper(WebAPIWrapper):
    backend: GravitateAPIClient
    forecast: GravitateAPIClient
    valuation: GravitateAPIClient


class PEWebAPIWrapper(WebAPIWrapper):
    integration: GravitateAPIClient


class RitaWebAPIWrapper(WebAPIWrapper):
    backend: GravitateAPIClient