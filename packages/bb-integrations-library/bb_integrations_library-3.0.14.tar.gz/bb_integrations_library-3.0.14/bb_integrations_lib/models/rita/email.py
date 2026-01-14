import base64
from typing import Optional

from pydantic import BaseModel, model_serializer, computed_field


class EmailAttachment(BaseModel):
    file_name: str
    file_data_encoded: Optional[str] = None

    def __init__(self, file_name: str, file_data: Optional[bytes] = None, file_data_encoded: Optional[str] = None):
        super().__init__(file_name=file_name)
        self.file_name = file_name
        self.file_data_encoded = self._b64enc(file_data) if file_data is not None else file_data_encoded

    def _b64enc(self, v) -> str:
        return base64.b64encode(v).decode("utf-8")

    @computed_field
    def file_data(self) -> bytes:
        return base64.b64decode(self.file_data_encoded)

    @file_data.setter
    def file_data(self, new_file_data: bytes) -> None:
        self.file_data_encoded = self._b64enc(new_file_data)

    @model_serializer()
    def serialize_model(self):
        return {
            "file_name": self.file_name,
            "file_data_encoded": self.file_data_encoded
        }


class EmailData(BaseModel):
    to: str | list[str]
    html_content: str
    subject: str
    attachments: Optional[list[EmailAttachment]] = None
