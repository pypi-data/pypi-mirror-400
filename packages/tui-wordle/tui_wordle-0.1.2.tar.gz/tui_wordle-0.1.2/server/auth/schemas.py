from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    id: int
    username: str
    token: str


# Google OAuth
class GoogleAuthUrlResponse(BaseModel):
    auth_url: str
    state: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: str


class GoogleCallbackResponse(BaseModel):
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    token: Optional[str] = None
    error: Optional[str] = None
