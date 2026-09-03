from fastapi import APIRouter

from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from app.services.auth_service import start_login, register_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    return start_login(request.email)

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    return register_user(request)