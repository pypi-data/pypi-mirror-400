from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class InstallationResponse(BaseModel):
    """Represents an individual photo or note response for a specific row."""
    type: Optional[int] = None
    photoId: Optional[str] = None
    photoName: Optional[str] = None
    note: Optional[str] = None
