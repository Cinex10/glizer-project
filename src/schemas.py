from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PubgRequest(BaseModel):
    email: str
    password: str
    player_id: str
    redeem_codes: List[str]

class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    message: str

class TransactionStatusResponse(BaseModel):
    transaction_id: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int
    max_retries: int
    result: Optional[dict] = None
    error_message: Optional[str] = None

class TransactionListItem(BaseModel):
    id: str
    email: str
    player_id: str
    status: str
    created_at: datetime
    retry_count: int

class HealthResponse(BaseModel):
    status: str
    active_threads: int
    max_workers: int
    thread_names: List[str]
