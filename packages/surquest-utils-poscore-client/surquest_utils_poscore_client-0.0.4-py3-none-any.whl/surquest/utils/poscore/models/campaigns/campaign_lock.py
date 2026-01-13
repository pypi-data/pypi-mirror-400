from __future__ import annotations
from pydantic import BaseModel


class CampaignLock(BaseModel):
    type: int
    isLocked: bool
