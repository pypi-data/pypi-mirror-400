from datetime import datetime, UTC

from pydantic import BaseModel

class SourceSystem(BaseModel):
    updated_by: str | None = None,
    updated_on: datetime | None = datetime.now(UTC)
    name: str
    description: str