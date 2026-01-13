from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class CampaignStatus(BaseModel):
    created: Optional[datetime] = None
    value: int
    name: str
