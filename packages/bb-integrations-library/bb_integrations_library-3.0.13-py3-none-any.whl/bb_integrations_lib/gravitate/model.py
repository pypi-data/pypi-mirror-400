from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, field_validator


class System(str, Enum):
    pe: str = "pricing_engine"
    sd: str = "supply_and_dispatch"
    rita: str = "rita"


class GravitateConfig(BaseModel):
    type: Optional[str] = None
    dbs: Optional[Dict[str, str]] = {}
    system_psk: Optional[str] = None
    conn_str: Optional[str] = None
    url: Optional[str] = None
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None
    system:Optional[System] = System.sd
    short_name: Optional[str] = None

    @field_validator("admin_username", "admin_password", "url", mode="before")
    @classmethod
    def strip_whitespace(cls, value):
        if value and isinstance(value, str):
            return value.strip()
        return value
