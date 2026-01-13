from __future__ import annotations
from pydantic import BaseModel


class SalesEmployee(BaseModel):
    id: int
    name: str
    email: str
