from typing import Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path
from starlette import status
from starlette.responses import JSONResponse

from app.core.security import get_user_id_by_token
from app.data.payment_constant import PaymentStatus
from app.services.payment_service import create_payment, retrieve_payment, approve_payment, update_payment

from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
)

@router.post("/create-payment")
def createPayment(request: CreatePaymentRequest, user_id: str = Depends(get_user_id_by_token)):
    print("Create payment request: ", request)
    print("User ID from token:", user_id)

    create_payment(request, user_id)
    response = JSONResponse(
        content= {
            "message": "Payment created",
        },
        status_code=status.HTTP_201_CREATED
    )
    return response

@router.get("/retrieve-payment")
def retrievePayment(user_id: str = Depends(get_user_id_by_token),
                    page_state: Optional[str] = Query(None),
                    size: int = Query(10, ge=0)):
    return retrieve_payment(UUID(user_id), page_state, size)


@router.patch("/approve-payment/{payment_id}")
def approvePayment(user_id: str = Depends(get_user_id_by_token),
                   payment_id: str = Path(),):
    print("Approve payment request: ", user_id)
    update_payment(UUID(user_id), UUID(payment_id), PaymentStatus.APPROVED.value)
    response = JSONResponse(
        content={
            "message": "Approved successfully",
        },
        status_code=status.HTTP_200_OK)
    return response

@router.patch("/reject-payment/{payment_id}")
def rejectPayment(user_id: str = Depends(get_user_id_by_token),
                   payment_id: str = Path(),):
    print("Reject payment request: ", user_id)
    update_payment(UUID(user_id), UUID(payment_id), PaymentStatus.REJECTED.value)
    response = JSONResponse(
        content={
            "message": "Rejected successfully",
        },
        status_code=status.HTTP_200_OK)
    return response