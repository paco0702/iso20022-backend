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
    full_name: Optional[str]

class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CurrentUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str]