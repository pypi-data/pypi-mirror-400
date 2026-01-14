from datetime import datetime
from enum import StrEnum
from typing import List

from pydantic import BaseModel


class ERPStatus(StrEnum):
    """Copied from supply_and_dispatch_aio 2025-06-17"""
    sent = "sent"
    unsent = "unsent"
    errors = "errors"

class BackofficeERP(BaseModel):
    """Copied from supply_and_dispatch_aio 2025-06-17"""
    status: ERPStatus = ERPStatus.unsent
    time_sent: datetime | None = None
    errors: List = []
