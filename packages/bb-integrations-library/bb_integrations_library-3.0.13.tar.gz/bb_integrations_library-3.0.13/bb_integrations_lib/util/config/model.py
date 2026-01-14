from typing import Optional, Dict

from bb_integrations_lib.gravitate.base_api import BaseAPI
from pydantic import BaseModel, Field, ConfigDict


class Config(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    psk: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    base_url: Optional[str] = None
    mongo_conn_str: Optional[str] = None
    mongo_db_name: Optional[str] = None
    extra_data: Optional[Dict] = Field(default_factory=dict)


class Configs(BaseModel):
    rita: Optional[Config] = Field(default_factory=Config)
    sd: Optional[Config] = Field(default_factory=Config)
    pe: Optional[Config] = Field(default_factory=Config)
    crossroads: Optional[Config] = Field(default_factory=Config)


class GlobalConfig(BaseModel):
    prod: Configs = Field(default_factory=Configs)
    test: Configs = Field(default_factory=Configs)
    extra_data: Optional[Dict] = Field(default_factory=dict)


class Client(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config
    api_client: BaseAPI


class ClientConstructor(BaseModel):
    rita:Client
    sd: Client
    pe: Client
