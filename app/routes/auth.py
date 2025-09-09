from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import LoginIn, TokenOut, RefreshIn
from ..security import verify_password, create_access_token, create_refresh_token, decode_token
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
def login(login_data: LoginIn, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user.email, user.role)
    refresh_token = create_refresh_token(user.email, user.role)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 1800
    }

@router.post("/refresh", response_model=TokenOut)
def refresh_token(data: RefreshIn):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("typ") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        email = payload.get("sub")
        role = payload.get("role")
        
        access_token = create_access_token(email, role)
        refresh_token = create_refresh_token(email, role)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me")
def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }