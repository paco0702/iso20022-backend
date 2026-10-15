from typing import Optional, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path
from starlette import status
from starlette.responses import JSONResponse

from app.core.security import get_user_id_by_token
from app.data.payment_constant import PaymentStatus
from app.services.payment_service import create_payment, retrieve_payment, update_payment, \
    retrieve_payment_by_debtor_iban, retrieve_payment_by_debtor_iban, create_batch

from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse, CreateBatchRequest

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
)

@router.post("/create-payment")
def createPayment(request: CreatePaymentRequest, user_id: str = Depends(get_user_id_by_token)):
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
                    status: str = PaymentStatus.PENDING.value,
                    page_state: Optional[str] = Query(None),
                    size: int = Query(10, ge=0)):
    return retrieve_payment(UUID(user_id), page_state, status, size)


@router.get("/retrieve-payment/{debtor_id}")
def retrievePayment(user_id: str = Depends(get_user_id_by_token),
                    status: str = PaymentStatus.PENDING.value,
                    debtor_id: str = Path(),
                    page_state: Optional[str] = Query(None),
                    size: int = Query(10, ge=0)):
    return retrieve_payment_by_debtor_iban(UUID(user_id), debtor_id, page_state, status, size)


@router.patch("/approve-payment/{payment_id}")
def approvePayment(user_id: str = Depends(get_user_id_by_token),
                   payment_id: str = Path(),):
    update_payment(UUID(user_id), UUID(payment_id), PaymentStatus.APPROVED.value)
    response = JSONResponse(
        content={
            "message": "Approved successfully",
        },
        status_code=status.HTTP_200_OK)
    return response

@router.delete("/reject-payment/{payment_id}")
def rejectPayment(user_id: str = Depends(get_user_id_by_token),
                   payment_id: str = Path(),):
    update_payment(UUID(user_id), UUID(payment_id), PaymentStatus.REJECTED.value)
    response = JSONResponse(
        content={
            "message": "Rejected successfully",
        },
        status_code=status.HTTP_200_OK)
    return response


@router.post("/create-batch")
async def createBatch(request: CreateBatchRequest,
                      user_id: str = Depends(get_user_id_by_token)):
    response = await create_batch(UUID(user_id), request)
    return JSONResponse(
        content={
            "status": "sent",
            "response": response
        },
        status_code=status.HTTP_200_OK)


