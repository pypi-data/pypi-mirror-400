from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class Partner(BaseModel):
    id: int
    name: str
    retailerAutoApprovalLimit: Optional[int] = None
