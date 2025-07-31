from pydantic import BaseModel
from typing import Literal

TransactionStatus = Literal["success", "error", "pending"]


class TransactionIDResponse(BaseModel):
    transactionsId: str


class TransactionStatusResponse(BaseModel):
    status: TransactionStatus


class GlizerWebhookPayload(BaseModel):
    event: Literal["ON_TRANSACTION_STATUS_CHANGED"] = "ON_TRANSACTION_STATUS_CHANGED"
    transactionsId: str
    status: TransactionStatus