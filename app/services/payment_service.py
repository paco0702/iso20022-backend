from typing import Optional, Literal
from uuid import UUID

from fastapi import HTTPException, Query

from app.repositories import payment_repository
from app.util import payment_util, datetime_util
from app.repositories.payment_repository import insert_payment_by_id, insert_payment_by_status
from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse, GetPaymentResponse
from app.data.payment_constant import (PaymentStatus)


def create_payment(request: CreatePaymentRequest, user_id):
    if request.id is None or request.id == '':
        raise HTTPException(status_code=400, detail="Payment id is required")

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
        "created_by": UUID(user_id),
        "updated_by": UUID(user_id),
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
        "status": PaymentStatus.PENDING.value,
    }

    inserted_by_id = insert_payment_by_id(payment)
    if not inserted_by_id:
        raise HTTPException(status_code=400, detail="Payment was not successful")

    inserted_by_status = insert_payment_by_status(payment)
    response = {
        "message": "success",
        "error": None,
    }
    return response


def retrieve_payment(user_id: UUID,
                     page_state: Optional[str],
                     size: int, ) -> GetPaymentResponse:
    result = payment_repository.get_payment_by_id(PaymentStatus.PENDING.value, page_state, user_id, size)

    return result


def update_payment(user_id: UUID, payment_id: UUID, payment_status: str):
    payment_exist = payment_repository.exist_payment_by_id(PaymentStatus.PENDING.value, payment_id, user_id)

    if not payment_exist:
        print("Payment does not exist")
        raise HTTPException(status_code=400, detail="Payment was not successful")

    pending_payment = payment_repository.get_payment_by_status(PaymentStatus.PENDING.value, payment_id, user_id)
    if not pending_payment:
        print("Pending Payment does not exist")
        raise HTTPException(status_code=400, detail="Payment was not successful")

    approved_by_id = payment_repository.update_payment_status_by_id(user_id, payment_status, payment_id)
    if not approved_by_id:
        print("Approved Payment does not exist")
        raise HTTPException(status_code=400, detail="Payment was not successful")

    payment_repository.remove_payment_by_status(PaymentStatus.PENDING.value, user_id, payment_id)

    payment = {
        "created_by": user_id,
        "updated_by": user_id,
        "id": pending_payment["id"],
        "amount": pending_payment["amount"],
        "currency": pending_payment["currency"],
        "creditor_name": pending_payment["creditor_name"],
        "creditor_bic": pending_payment["creditor_bic"],
        "creditor_iban": pending_payment["creditor_iban"],
        "debtor_name": pending_payment["debtor_name"],
        "debtor_bic": pending_payment["debtor_bic"],
        "debtor_iban": pending_payment["debtor_iban"],
        "execute_date": pending_payment["execute_date"],
        "transaction_no": pending_payment["transaction_no"],
        "message_id": pending_payment["message_id"],
        "initial_party": pending_payment["initial_party"],
        "code": pending_payment["code"],
        "invoice_number": pending_payment["invoice_number"],
        "created_at": pending_payment["created_at"],
        "updated_at": pending_payment["updated_at"],
        "charge_bearer": pending_payment["charge_bearer"],
        "remittance": pending_payment["remittance"],
        "end_to_end_id": pending_payment["end_to_end_id"],
        "status": payment_status,
    }
    inserted_by_status = insert_payment_by_status(payment)
    if not inserted_by_status:
        print("Insert payment by status failed")
        raise HTTPException(status_code=400, detail="Payment was not successful")


