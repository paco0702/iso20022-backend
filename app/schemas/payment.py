from datetime import datetime
from uuid import UUID

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


class PaymentBatchItem(BaseModel):
    id: str
    batch_type: str
    batch_id: str
    xml_content: str
    batch_name: str
    payment_ids: List[UUID]
    total_amount: float
    created_at: str
    updated_at: str
    updated_by: str
    created_by: str

class GetPaymentResponse(BaseModel):
    items: List[PaymentItem]
    pagination: Pagination

class CreateBatchRequest(BaseModel):
    batch_id: str
    batch_file_name: str
    xml_content: str
    created_at: datetime
    payment_ids: List[str]


class GetPaymentBatchResponse(BaseModel):
    items: List[PaymentBatchItem]
    pagination: Pagination

class GetPaymentBatchOverview(BaseModel):
    total_count: int
    total_pending_approval: int
    total_validation_failed: int
    total_amount: float