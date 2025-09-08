from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import Hasher, create_token
from app.schemas.auth import TokenPair, LoginIn
from app.schemas.user import UserCreate, UserOut
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=Hasher.hash(payload.password),
        is_driver=payload.is_driver,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not Hasher.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_token(
        {"sub": str(user.id), "scope": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh = create_token(
        {"sub": str(user.id), "scope": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return {"access_token": access, "refresh_token": refresh}
