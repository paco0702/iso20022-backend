from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse
from app.services.payment_service import create_payment

from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
)

@router.post("/create-payment")
def payment(request: CreatePaymentRequest):
    print("Create payment request: ", request)
    create_payment(request)
    response = JSONResponse(
        content= {
            "message": "Payment created",
        },
        status_code=status.HTTP_201_CREATED
    )
    return response