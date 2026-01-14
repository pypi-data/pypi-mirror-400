from typing import List
from fastapi import Query

from pydantic import BaseModel, EmailStr


class DomainInfo(BaseModel):
    domain: str
    role: str

class User(BaseModel):
    email: EmailStr
    password: str | None = None
    source: str = ""
    disabled: bool = False
    access: List[DomainInfo]
    password_reset_code: str | None = None


class Role(BaseModel):
    name: str
    scopes: List[str] = []


class RequireScope:
    def __init__(self, scope: str):
        self.scope = scope

    def __call__(self, scopes: str = Query(...)):
        return self.scope in scopes.split(",")
