from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    CANCELED = "CANCELED"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), index=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    seats: Mapped[int]
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ride = relationship("Ride", back_populates="bookings")
    passenger = relationship("User", back_populates="bookings")
