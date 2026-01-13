from __future__ import annotations
from typing import List
from pydantic import BaseModel
from .campaign_row_installation import CampaignRowInstallation


class LocationInstallation(BaseModel):
    """Represents a physical store location and the associated campaign rows."""
    id: int
    identifier: str
    city: str
    street: str
    zip: str
    rows: List[CampaignRowInstallation]
