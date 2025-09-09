import time
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(sub: str, role: str, expires: Optional[int] = None) -> str:
    exp = int(time.time()) + (expires or settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": sub, "role": role, "exp": exp, "typ": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(sub: str, role: str, expires: Optional[int] = None) -> str:
    exp = int(time.time()) + (expires or settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": sub, "role": role, "exp": exp, "typ": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")