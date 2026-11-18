import uuid
from typing import Optional, Literal
from uuid import UUID
from zipfile import error

import httpx
from fastapi import HTTPException, Query
from starlette import status

from app.repositories import payment_repository
from app.util import payment_util, datetime_util, xml_util
from app.repositories.payment_repository import (insert_payment_by_id, insert_payment_by_status, get_payment_by_status_and_debtor_iban, all_payment_by_ids_exists,
                                                 insert_payment_batch_by_id, count_payment_batch_by_type, count_payment_batch, count_payment_batch_total_amount, get_total_amount_by_payment_ids,
                                                 update_status_payment_by_id_by_ids, update_status_payment_by_status_by_ids, get_batch_by_batch_id, get_payment_by_ids)
from app.schemas.payment import CreatePaymentRequest, CreatePaymentResponse, GetPaymentResponse, CreateBatchRequest
from app.data.payment_constant import (PaymentStatus)
import re

BANK_SERVICE_URL = "http://localhost:8001/payment/receive-xml"

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

    # created_at = datetime_util.to_iso_8601_format(request.creation_date)
    # execute_date = datetime_util.to_iso_8601_format(request.execute_date)
    request_id = UUID(request.id)
    converted_amount = payment_util.convert_amount_to_hkd(request.amount, request.currency)

    payment = {
        "created_by": UUID(user_id),
        "updated_by": UUID(user_id),
        "id": request_id,
        "amount": converted_amount,
        "currency": request.currency,
        "creditor_name": request.creditor_name,
        "creditor_bic": request.creditor_bic,
        "creditor_iban": request.creditor_iban,
        "debtor_name": request.debtor_name,
        "debtor_bic": request.debtor_bic,
        "debtor_iban": request.debtor_iban,
        "execute_date": request.execute_date,
        "transaction_no": request.transaction_no,
        "message_id": request.message_id,
        "initial_party": request.initial_party,
        "code": request.code,
        "invoice_number": request.invoice_number,
        "created_at": request.creation_date,
        "updated_at": request.creation_date,
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
                     status: str,
                     size: int, ) -> GetPaymentResponse:
    result = payment_repository.get_payment_by_user_id_and_status(user_id, status, page_state, size)

    return result

def retrieve_payment_by_debtor_iban(user_id: UUID,
                     debtor_id: str,
                     page_state: Optional[str],
                     status: str,
                     size: int,) -> GetPaymentResponse:
    result = payment_repository.get_payment_by_status_and_debtor_iban(status, debtor_id,  page_state, user_id, size)

    return result


def update_payment(user_id: UUID, payment_id: UUID, payment_status: str):
    payment_exist = payment_repository.exist_payment_by_id(PaymentStatus.PENDING.value, payment_id, user_id)
    updated_at = datetime_util.updated_datetime()
    if not payment_exist:
        print("Payment does not exist")
        raise HTTPException(status_code=400, detail="Payment was not successful")

    pending_payment = payment_repository.get_payment_by_status_and_id(PaymentStatus.PENDING.value, payment_id, user_id)
    if not pending_payment:
        print("Pending Payment does not exist")
        raise HTTPException(status_code=400, detail="Payment was not successful")

    approved_by_id = payment_repository.update_payment_id_by_id(user_id, payment_status, payment_id, updated_at)
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



async def create_batch (user_id: UUID, request: CreateBatchRequest):
    if not request.payment_ids:
        raise HTTPException(status_code=400, detail="Empty payment list.")

    converted_payment_ids = [UUID(payment_id) for payment_id in request.payment_ids]
    exists_all = all_payment_by_ids_exists(converted_payment_ids)
    payment_amounts = get_total_amount_by_payment_ids(converted_payment_ids)
    total_amount = 0
    print("Payment amounts", payment_amounts)
    for amount in payment_amounts:
        converted_amount = payment_util.convert_amount_to_hkd(float(amount['amount']), amount['currency'])
        total_amount += converted_amount

    cleaned_xml_content = xml_util.clean_up_xml_content(request.xml_content)
    request.xml_content = cleaned_xml_content

    if not exists_all:
        raise HTTPException(status_code=400, detail="Not all payment ids exist")


    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                BANK_SERVICE_URL,
                content=request.model_dump_json(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            confirmed_xml_content = xml_util.clean_up_xml_content(response.json().get("return_xml_message"))
            if response.json().get("return_xml_message") is None or response.json().get("payment_results") is None:
                raise HTTPException(status_code=400, detail="Payment was not successful")

            batch_status = "created"
            # retrieve bank status
            all_accepted = all(
                payment["payment_status"] == "accepted"
                for payment in response.json().get("payment_results")
            )

            all_rejected = all(
                payment["payment_status"] == "rejected"
                for payment in response.json().get("payment_results")
            )

            if all_accepted:
                batch_status = "accepted"

            if all_rejected:
                batch_status = "rejected"

            if not all_accepted and not all_rejected:
                batch_status = "partial_accepted"

            print("converted payment ids:", converted_payment_ids)
            payment_batch = {
                "id": uuid.uuid4(),
                "batch_id": request.batch_id,
                "batch_message": confirmed_xml_content,
                "batch_name": request.batch_file_name,
                "batch_type": batch_status,
                "created_at": request.created_at,
                "created_by": user_id,
                "updated_at": request.created_at,
                "updated_by": user_id,
                "payment_ids": converted_payment_ids,
                "total_amount": total_amount,
            }
            insert_payment_batch_by_id(payment_batch)
            updated_at =  datetime_util.updated_datetime()

            for payment_result in response.json().get("payment_results"):
                payment_id = uuid.UUID(payment_result["payment_id"])
                payment = payment_repository.get_payment_by_status_and_id("approved", payment_id, user_id)
                payment_repository.remove_payment_by_status("approved", user_id, payment_id)
                payment["status"] = payment_result.get("payment_status")
                payment_repository.insert_payment_by_status(payment)
                payment_repository.update_payment_id_by_id(user_id, payment_result.get("payment_status"), payment_id, updated_at)
            return response.json()
        except error:
            payment_batch = {
                "id": uuid.uuid4(),
                "batch_id": request.batch_id,
                "batch_message": request.xml_content,
                "batch_name": request.batch_file_name,
                "batch_type": "failed",
                "created_at": request.created_at,
                "created_by": user_id,
                "updated_at": request.created_at,
                "updated_by": user_id,
                "payment_ids": converted_payment_ids,
            }
            insert_payment_batch_by_id(payment_batch)
            update_status_payment_by_status_by_ids(user_id, PaymentStatus.REJECTED.value, converted_payment_ids)
            update_status_payment_by_id_by_ids(user_id, PaymentStatus.REJECTED.value, converted_payment_ids)
            return response.json()

def retrieve_payment_batch (user_id: UUID,
    page_state: Optional[str],
    size: int):
    result = payment_repository.get_payment_batch_by_user_id(user_id, page_state, size)
    return result


def retrieve_batch_overview (user_id: UUID):
    #TODO: check user id for future usage
    pending_approval_batch = count_payment_batch_by_type("accepted")
    validation_failed_batch = count_payment_batch_by_type("failed")
    total_payment_batch = count_payment_batch()
    total_payment_amount = count_payment_batch_total_amount()


    return {
        "pending_approval_batch": pending_approval_batch,
        "validation_failed_batch": validation_failed_batch,
        "total_payment_batch": total_payment_batch,
        "total_payment_amount": total_payment_amount
    }

def retrieve_batch_by_batch_id (user_id: UUID, batch_id: str):
    batch = get_batch_by_batch_id(batch_id)

    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)

    payment_ids = batch["payment_ids"]

    if payment_ids is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,)

    payments = get_payment_by_ids(payment_ids, user_id)
    no_of_rejected = 0
    no_of_accepted = 0

    for payment in payments:
        if payment.status == "rejected":
            no_of_rejected += 1
        if payment.status == "accepted":
            no_of_accepted += 1

    batch["no_of_rejected"] = no_of_rejected
    batch["no_of_accepted"] = no_of_accepted

    return {
        "batch_details": batch,
        "batch_payments": payments,
    }