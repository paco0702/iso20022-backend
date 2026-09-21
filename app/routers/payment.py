from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from app.core.security import get_user_id_by_token
from app.services.payment_service import create_payment

from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
)

@router.post("/create-payment")
def payment(request: CreatePaymentRequest, user_id: str = Depends(get_user_id_by_token)):
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