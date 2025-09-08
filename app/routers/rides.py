from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.ride import Ride, RideStatus
from app.models.user import User
from app.schemas.ride import RideCreate, RideOut
from .users import get_current_user

router = APIRouter(prefix="/rides", tags=["rides"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RideOut)
def create_ride(payload: RideCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.is_driver:
        raise HTTPException(status_code=403, detail="Only drivers can create rides")
    ride = Ride(
        driver_id=user.id,
        origin=payload.origin,
        destination=payload.destination,
        departure_time=payload.departure_time,
        seats_available=payload.seats_available,
        price=payload.price,
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return ride

@router.get("/search", response_model=List[RideOut])
def search_rides(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    earliest: Optional[datetime] = None,
    latest: Optional[datetime] = None,
    skip: int = 0,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Ride).filter(Ride.status == RideStatus.OPEN)
    if origin:
        q = q.filter(Ride.origin.ilike(f"%{origin}%"))
    if destination:
        q = q.filter(Ride.destination.ilike(f"%{destination}%"))
    if earliest:
        q = q.filter(Ride.departure_time >= earliest)
    if latest:
        q = q.filter(Ride.departure_time <= latest)
    return q.order_by(Ride.departure_time.asc()).offset(skip).limit(limit).all()
