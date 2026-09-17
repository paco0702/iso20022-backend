from authlib.oauth2.rfc6749.grants import refresh_token
from fastapi import APIRouter, Response, HTTPException, status, Request

from app.schemas.auth import RefreshTokenRequest
from app.services import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/refresh")
def refresh_access_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    return auth_service.refresh_user_token(refresh_token=refresh_token)