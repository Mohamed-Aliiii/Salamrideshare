from datetime import datetime, timedelta
import jwt
from passlib.hash import argon2
from app.core.config import settings

ALGORITHM = settings.JWT_ALG
SECRET_KEY = settings.JWT_SECRET

class Hasher:
    @staticmethod
    def hash(pw: str) -> str:
        return argon2.hash(pw)

    @staticmethod
    def verify(pw: str, hashed: str) -> bool:
        return argon2.verify(pw, hashed)

def create_token(subject: dict, expires_delta: timedelta) -> str:
    to_encode = subject.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
