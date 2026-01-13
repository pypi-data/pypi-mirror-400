from __future__ import annotations
from typing import List
from pydantic import BaseModel
from .location_installation import LocationInstallation


class InstallationStatusPayload(BaseModel):
    """The top-level object categorizing locations by their installation state."""
    inProgress: List[LocationInstallation] = []
    pendingReview: List[LocationInstallation] = []
    partiallyInstalled: List[LocationInstallation] = []
    unsuccessful: List[LocationInstallation] = []
    installed: List[LocationInstallation] = []
    missed: List[LocationInstallation] = []
