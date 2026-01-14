from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Bucket(BaseModel):
    """
    Bucket is a grouping mechanism. It may reference another bucket as its container
    Items may reference a bucket as their container, but an item can only be contained in one bucket.
    """
    owned_by: Optional[str] = None # TODO: Write a validator that checks for cycles
    name: str
    description: Optional[str] = None
    updated_by: Optional[str] = None
    updated_on: Optional[datetime] = None
    is_active: bool = True
