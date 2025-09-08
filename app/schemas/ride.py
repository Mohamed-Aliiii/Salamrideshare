from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RideCreate(BaseModel):
    origin: str
    destination: str
    departure_time: datetime
    seats_available: int
    price: float

class RideOut(BaseModel):
    id: int
    driver_id: int
    origin: str
    destination: str
    departure_time: datetime
    seats_available: int
    price: float
    status: str
    class Config:
        from_attributes = True
