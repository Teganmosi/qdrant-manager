from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Any, Dict
from .enums import RoleEnum, DistanceEnum
from datetime import datetime
import re

class LoginIn(BaseModel):
    """Input schema for user login."""
    email: EmailStr
    password: str = Field(min_length=8)

    @validator("password")
    def validate_password(cls, v):
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", v):
            raise ValueError("Password must contain at least one lowercase, uppercase, and digit")
        return v

class TokenOut(BaseModel):
    """Output schema for JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshIn(BaseModel):
    """Input schema for token refresh."""
    refresh_token: str

class UserCreateIn(BaseModel):
    """Input schema for creating a user."""
    email: EmailStr
    password: str = Field(min_length=8)
    role: RoleEnum = RoleEnum.VIEWER

    @validator("password")
    def validate_password(cls, v):
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", v):
            raise ValueError("Password must contain at least one lowercase, uppercase, and digit")
        return v

class UserOut(BaseModel):
    """Output schema for user data."""
    id: int
    email: EmailStr
    role: RoleEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CollectionCreateIn(BaseModel):
    """Input schema for creating a Qdrant collection."""
    name: str = Field(max_length=255, pattern=r"^[a-zA-Z0-9_-]+$")  # FIXED: regex -> pattern
    vector_size: int = Field(ge=1)
    distance: DistanceEnum = DistanceEnum.COSINE

class PointUpsertIn(BaseModel):
    """Input schema for upserting a Qdrant point."""
    collection: str = Field(max_length=255, pattern=r"^[a-zA-Z0-9_-]+$")  # FIXED: regex -> pattern
    id: int = Field(ge=1)
    vector: List[float]
    payload: Dict[str, Any] = {}

    @validator("vector")
    def validate_vector(cls, v):
        if not all(isinstance(x, (int, float)) and -1e9 <= x <= 1e9 for x in v):
            raise ValueError("Vector elements must be numbers within reasonable bounds")
        return v

    @validator("payload")
    def validate_payload(cls, v):
        if len(str(v)) > 10_000:
            raise ValueError("Payload size exceeds maximum limit")
        return v

class PointsDeleteIn(BaseModel):
    """Input schema for deleting Qdrant points."""
    collection: str = Field(max_length=255, pattern=r"^[a-zA-Z0-9_-]+$")  # FIXED: regex -> pattern
    ids: List[int] = Field(min_items=1)

class VectorSearchIn(BaseModel):
    """Input schema for Qdrant vector search."""
    collection: str = Field(max_length=255, pattern=r"^[a-zA-Z0-9_-]+$")  # FIXED: regex -> pattern
    vector: List[float]
    limit: int = Field(ge=1, le=100, default=10)
    with_payload: bool = True
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)

    @validator("vector")
    def validate_vector(cls, v):
        if not all(isinstance(x, (int, float)) and -1e9 <= x <= 1e9 for x in v):
            raise ValueError("Vector elements must be numbers within reasonable bounds")
        return v