from __future__ import annotations
from typing import List
from pydantic import BaseModel


class Component(BaseModel):
    id: int
    name: str
    carrierId: int
    partners: List[dict] = []
