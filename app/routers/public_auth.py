from authlib.oauth2.rfc6749.grants import refresh_token
from fastapi import APIRouter, Response, HTTPException, status
from starlette.responses import JSONResponse

from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, CheckEmailResponse, CheckEmailRequest
from app.services.auth_service import start_login, register_user, validate_email
from pydantic import EmailStr

router = APIRouter(
    prefix="/public",
    tags=["Auth"],
)

@router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response):
    loginResponse = start_login(request)
    response = JSONResponse (
        content = {
            "access_token": loginResponse["access_token"],
            "user_id": str(loginResponse["user_id"]),
            "email": loginResponse["email"],
            "full_name_en": loginResponse["full_name_en"],
            "full_name_ch": loginResponse["full_name_ch"],
            "created_at": str(loginResponse["created_at"]),
            "updated_at": str(loginResponse["updated_at"]),
            "refresh_token": loginResponse["refresh_token"],
        }
    )
    response.set_cookie(
        key="refresh_token",
        value= loginResponse["refresh_token"],
        httponly=True,
        secure=False,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/auth/refresh",
    )
    return response

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        path="/auth/refresh",
    )
    return {
        "message": "Logged out successfully"
    }

@router.get('/validate-email', response_model=CheckEmailResponse)
def validate_email(email: EmailStr):
    return validate_email(email)

@router.post("/auth/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    return register_user(request)