from uuid import UUID

from fastapi import HTTPException
from app.util import payment_util, datetime_util
from app.repositories.payment_repository import insert_payment_by_id
from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse

def create_payment(request: CreatePaymentRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    if request.creditor_iban is None or request.debtor_iban is None:
        raise HTTPException(status_code=400, detail="Creditor and debtor must be set")

    if (request.debtor_iban == request.creditor_iban) or ():
        raise HTTPException(status_code=400, detail="Creditor and debtor IBAN must be valid")

    if (not payment_util.is_valid_iban(request.creditor_iban)) or (not payment_util.is_valid_iban(request.debtor_iban)):
        raise HTTPException(status_code=400, detail="Creditor IBAN must be valid")

    created_at = datetime_util.to_iso_8601_format(request.creation_date)
    execute_date = datetime_util.to_iso_8601_format(request.execute_date)
    request_id = UUID(request.id)
    payment = {
        "id": request_id,
        "amount": request.amount,
        "currency": request.currency,
        "creditor_name": request.creditor_name,
        "creditor_bic": request.creditor_bic,
        "creditor_iban": request.creditor_iban,
        "debtor_name": request.debtor_name,
        "debtor_bic": request.debtor_bic,
        "debtor_iban": request.debtor_iban,
        "execute_date": execute_date,
        "transaction_no": request.transaction_no,
        "message_id": request.message_id,
        "initial_party": request.initial_party,
        "code": request.code,
        "invoice_number": request.invoice_number,
        "created_at": created_at,
        "updated_at": created_at,
        "charge_bearer": request.charge_bearer,
        "remittance": request.remittance,
        "end_to_end_id": request.end_to_end_id,
    }

    inserted_by_id = insert_payment_by_id(payment)
    if not inserted_by_id:
        raise HTTPException(status_code=400, detail="Payment was not successful")

    response = {
        "message": "success",
        "error": None,
    }
    return response