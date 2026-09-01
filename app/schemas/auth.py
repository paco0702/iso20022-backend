from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    message: str
    email: EmailStr

