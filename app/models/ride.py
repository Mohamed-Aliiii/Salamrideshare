from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class RideStatus(str, enum.Enum):
    OPEN = "OPEN"
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    origin: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    departure_time: Mapped[datetime] = mapped_column(DateTime)
    seats_available: Mapped[int]
    price: Mapped[float] = mapped_column(Numeric(10,2))
    status: Mapped[RideStatus] = mapped_column(Enum(RideStatus), default=RideStatus.OPEN)

    driver = relationship("User", back_populates="rides")
    bookings = relationship("Booking", back_populates="ride", cascade="all, delete-orphan")
