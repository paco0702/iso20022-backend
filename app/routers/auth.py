from fastapi import APIRouter

from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, CheckEmailResponse, CheckEmailRequest
from app.services.auth_service import start_login, register_user, validate_email
from pydantic import EmailStr

router = APIRouter(
    prefix="/public",
    tags=["Auth"],
)

@router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    print ("request: ", request)
    return start_login(request)

@router.get('/validate-email', response_model=CheckEmailResponse)
def validate_email(email: EmailStr):
    return validate_email(email)

@router.post("/auth/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    return register_user(request)