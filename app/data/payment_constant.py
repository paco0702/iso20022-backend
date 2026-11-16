from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    APPROVED = "approved"
    ACCEPTED = "accepted"
    PARTIALLY_ACCEPTED = "partially_rejected"
    SETTLED = "settled"
    RECONCILED = "reconciled"
