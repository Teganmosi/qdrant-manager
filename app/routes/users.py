from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..schemas import UserCreateIn, UserOut
from ..deps import get_current_user, require_role
from ..models import User
from ..security import hash_password
from ..db import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut)
def create_user(
    data: UserCreateIn,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_password = hash_password(data.password)
    user = User(
        email=data.email,
        hashed_password=hashed_password,
        role=data.role.value
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.get("", response_model=list[UserOut])
def list_users(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"status": "success", "message": f"User {user_id} deleted"}