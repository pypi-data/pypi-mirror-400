from __future__ import annotations
from pydantic import BaseModel


class Carrier(BaseModel):
    id: int
    name: str
    allowReservation: bool
