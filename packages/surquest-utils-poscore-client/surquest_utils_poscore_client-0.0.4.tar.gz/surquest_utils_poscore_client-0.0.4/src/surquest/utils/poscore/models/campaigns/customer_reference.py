from __future__ import annotations
from pydantic import BaseModel


class CustomerReference(BaseModel):
    id: int
    name: str
    code: str
