from fastapi import APIRouter

from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import start_login

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    return start_login(request.email)