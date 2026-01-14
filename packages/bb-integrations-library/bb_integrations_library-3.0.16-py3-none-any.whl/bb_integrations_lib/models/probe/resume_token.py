from pydantic import BaseModel


class ResumeToken(BaseModel):
    probe_id: str
    resume_token: dict
    resume_token_timestamp: str  # isoformat, UTC