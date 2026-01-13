from __future__ import annotations
from pydantic import BaseModel, computed_field
import uuid


class Blob(BaseModel):
    id: str | int | uuid.UUID
    file_name: str
    content_type: str
    content: bytes

    @computed_field
    @property
    def size(self) -> int:
        """Size of the content in bytes."""
        return len(self.content)
