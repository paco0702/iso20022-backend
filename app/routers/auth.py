from authlib.oauth2.rfc6749.grants import refresh_token
from fastapi import APIRouter, Response, HTTPException, status

from app.schemas.auth import RefreshTokenRequest
from app.services import auth_service
from app.services.auth_service import start_login, register_user, validate_email
from pydantic import EmailStr

router = APIRouter(
    prefix="/public",
    tags=["Auth"],
)

@router.post("/refresh")
def refresh_access_token(request: RefreshTokenRequest):
    return auth_service.refresh_user_token(request=request)