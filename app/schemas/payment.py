from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List
from app.schemas.common import (Pagination)


class CreatePaymentRequest(BaseModel):
    id: str
    amount: float
    currency: str
    execute_date: str
    end_to_end_id: str
    remittance: str
    charge_bearer: str
    debtor_name: str
    debtor_iban: str
    debtor_bic: Optional[str]
    creditor_name: str
    creditor_iban: str
    creditor_bic: Optional[str]
    creation_date: str
    message_id: str
    initial_party: str
    transaction_no: int
    code: str
    invoice_number: str


class CreatePaymentResponse(BaseModel):
    message: str
    error: Optional[str]


class PaymentItem(BaseModel):
    id: str
    status: str
    created_at: datetime
    amount: float
    currency: str
    execute_date: datetime
    end_to_end_id: str
    remittance: str
    charge_bearer: str
    debtor_name: str
    debtor_iban: str
    debtor_bic: Optional[str]
    creditor_name: str
    creditor_iban: str
    creditor_bic: Optional[str]
    created_by: str
    updated_by: str
    transaction_no: int


class GetPaymentResponse(BaseModel):
    items: List[PaymentItem]
    pagination: Pagination
