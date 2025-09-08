from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.ride import Ride, RideStatus
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from .users import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=BookingOut)
def request_booking(payload: BookingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ride = db.get(Ride, payload.ride_id)
    if not ride or ride.status not in [RideStatus.OPEN, RideStatus.REQUESTED]:
        raise HTTPException(status_code=400, detail="Ride not available")
    if payload.seats <= 0 or payload.seats > ride.seats_available:
        raise HTTPException(status_code=400, detail="Invalid seats requested")
    booking = Booking(ride_id=ride.id, passenger_id=user.id, seats=payload.seats)
    ride.status = RideStatus.REQUESTED
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{booking_id}/accept", response_model=BookingOut)
def accept_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    ride = db.get(Ride, booking.ride_id)
    if ride.driver_id != user.id:
        raise HTTPException(status_code=403, detail="Only the driver can accept")
    if booking.seats > ride.seats_available:
        raise HTTPException(status_code=400, detail="Not enough seats available")
    booking.status = BookingStatus.ACCEPTED
    ride.seats_available -= booking.seats
    ride.status = RideStatus.ACCEPTED
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/{booking_id}/decline", response_model=BookingOut)
def decline_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    ride = db.get(Ride, booking.ride_id)
    if ride.driver_id != user.id:
        raise HTTPException(status_code=403, detail="Only the driver can decline")
    booking.status = BookingStatus.DECLINED
    # If all bookings declined, ride can go back to OPEN
    any_pending = db.query(Booking).filter(Booking.ride_id == ride.id, Booking.status == BookingStatus.PENDING).first()
    if not any_pending:
        ride.status = RideStatus.OPEN
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/rides/{ride_id}/start")
def start_ride(ride_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ride = db.get(Ride, ride_id)
    if not ride or ride.driver_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found or unauthorized")
    ride.status = RideStatus.IN_PROGRESS
    db.commit()
    return {"status": ride.status}

@router.post("/rides/{ride_id}/complete")
def complete_ride(ride_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ride = db.get(Ride, ride_id)
    if not ride or ride.driver_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found or unauthorized")
    ride.status = RideStatus.COMPLETED
    db.commit()
    return {"status": ride.status}
