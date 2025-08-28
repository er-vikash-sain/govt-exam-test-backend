from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    phone: Optional[str] = None
    role: str
    status: str
    locale: str
    timezone: str
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    role: str = "student"
    locale: str = "en_IN"
    timezone: str = "Asia/Kolkata"

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state_id: Optional[uuid.UUID] = None
    education_level: Optional[str] = None
    current_institution: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state_id: Optional[uuid.UUID] = None
    education_level: Optional[str] = None
    current_institution: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
