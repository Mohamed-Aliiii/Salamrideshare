from pydantic import BaseModel
from datetime import datetime

class BookingCreate(BaseModel):
    ride_id: int
    seats: int

class BookingOut(BaseModel):
    id: int
    ride_id: int
    passenger_id: int
    seats: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True
