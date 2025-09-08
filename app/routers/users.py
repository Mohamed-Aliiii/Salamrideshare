from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import jwt
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

SECRET = settings.JWT_SECRET
ALG = settings.JWT_ALG

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALG])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
