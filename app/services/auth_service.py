from datetime import datetime, timezone
from uuid import uuid4

from jose import JWTError
from pydantic import EmailStr

from app.core.config import Settings
from app.repositories.user_repository import (insert_user_by_email, insert_user_by_id, delete_user_by_email, get_user_by_email)
from app.repositories.user_repair_repository import (upsert_user_repair_task)
from app.schemas.auth import RegisterRequest, LoginRequest, LoginResponse, RefreshTokenRequest
from fastapi import HTTPException, status, Response
from app.core.security import (hash_password, verify_password, create_access_token, create_refresh_token, decode_token)

def start_login(request: LoginRequest):
    user = get_user_by_email(request.email)

    if request.email is None or request.email == "" or request.password is None or request.password == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or password not provided"
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password not match"
        )

    access_token = create_access_token(str(user["id"]), user["email"])
    refresh_token = create_refresh_token(str(user["id"]), user["email"])
    print("refresh token: ", refresh_token)
    response = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "email": user["email"],
        "full_name_en": user["full_name_en"],
        "full_name_ch": user["full_name_ch"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }
    return response

def validate_email(email: EmailStr):
    user = get_user_by_email(email)
    # if user exist, then email is not valid
    if not user is not None:
        return False
    else :
        return True

def register_user(request: RegisterRequest):
    """
    :param request:
    :return:
    """
    """ TODO: validate request """

    user = {
        "id": uuid4(),
        "email": request.email,
        "full_name_en": request.full_name_en,
        "full_name_ch": request.full_name_ch if request.full_name_ch is not None else request.full_name_en,
        "hashed_password": hash_password(request.password),
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    applied_by_email = insert_user_by_email(user)

    print("applied by email: ", applied_by_email)
    if not applied_by_email:
       raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Register information not valid")

    applied_by_id = insert_user_by_id(user)
    if not applied_by_id:
        if applied_by_email:
            delete_user_by_email(user["email"])

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register information not valid"
        )

    return user
    # try:
    #     applied = retry (
    #         lambda: insert_user(user),
    #         retries=3,
    #         initial_delay_second=0.1
    #     )
    #     inserted = True
    #     print("applied", applied)
    #     if not applied:
    #         raise HTTPException(
    #             status_code=status.HTTP_409_BAD_REQUEST,
    #             detail="Register information not valid")
    #
    #     # other extra function
    # except Exception as exc:
    #     if inserted:
    #         rollback_inserted_record(user)
    #     upsert_user_repair_task(
    #         user,
    #         reason="Failed to insert users_by_id during registration",
    #         last_error=str(exc)
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="User registration is temporarily unavailable. Please try again later."
    #     )

def refresh_user_token(request: RefreshTokenRequest):
    refresh_token = request.refresh_token
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    try:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        new_access_token = create_access_token(
            user_id=user_id,
            email=email,
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

