from __future__ import annotations
from pydantic import BaseModel


class Contact(BaseModel):
    id: int
    name: str
    email: str
    phone: str
