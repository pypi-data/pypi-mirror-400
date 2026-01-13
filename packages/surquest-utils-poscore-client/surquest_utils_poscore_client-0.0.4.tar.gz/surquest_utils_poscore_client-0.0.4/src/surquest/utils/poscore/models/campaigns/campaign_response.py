from __future__ import annotations
from typing import List
from pydantic import BaseModel

from .campaign import Campaign


class CampaignResponse(BaseModel):
    currentPage: int
    pageSize: int
    rowCount: int
    pageCount: int
    data: List[Campaign]
