from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    message: str
    email: EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name_en: str
    full_name_ch: Optional[str] = None


class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name_en: str
    full_name_ch: Optional[str]
    hashed_password: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CurrentUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name_en: Optional[str]