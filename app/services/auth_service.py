from datetime import datetime, timezone
from uuid import uuid4

from pydantic import EmailStr
from app.repositories.user_repository import (insert_user_by_email, insert_user_by_id, insert_user,
                                              rollback_inserted_record, delete_user_by_email, get_user_by_email, get_user_by_email_and_password)
from app.repositories.user_repair_repository import (upsert_user_repair_task)
from app.schemas.auth import RegisterRequest, LoginRequest, LoginResponse

from fastapi import HTTPException, status
from app.core.retry import retry
from app.util.encod_util import hash_password

def start_login(request: LoginRequest):
    get_user_by_email_and_password(request.email, hash_password(request.password))

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


