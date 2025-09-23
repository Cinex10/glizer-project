"""
Schémas Pydantic adaptés pour les bots 9 et 10
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class BotTransactionResponse(BaseModel):
    transaction_id: str
    bot_num: int
    status: str
    message: str

class BotTransactionStatusResponse(BaseModel):
    transaction_id: str
    bot_num: int
    status: str
    created_at: Optional[datetime] = None  # Colonne supprimée dans nouvelle architecture
    started_at: Optional[datetime] = None  # Colonne supprimée dans nouvelle architecture
    completed_at: Optional[datetime] = None  # Colonne supprimée dans nouvelle architecture
    retry_count: int = 0  # Colonne supprimée dans nouvelle architecture
    max_retries: int = 0  # Colonne supprimée dans nouvelle architecture
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    player_id: Optional[str] = None
    redeem_codes: Optional[List[str]] = None

class BotTransactionListItem(BaseModel):
    id: str
    bot_num: int
    status: str
    created_at: Optional[datetime] = None  # Colonne supprimée dans nouvelle architecture
    updated_at: Optional[datetime] = None  # Colonne supprimée dans nouvelle architecture
    retry_count: int = 0  # Colonne supprimée dans nouvelle architecture
    player_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    active_threads: int
    max_workers: int
    thread_names: List[str]

class BotStatsResponse(BaseModel):
    bot_num: int
    total_transactions: int
    pending: int
    processing: int
    success: int
    failed: int
    success_rate: float

class SystemStatsResponse(BaseModel):
    system_status: str
    bots: Dict[str, BotStatsResponse]
    totals: Dict[str, int]
    thread_manager: Dict[str, Any]

class ProcessResultResponse(BaseModel):
    transaction_id: str
    status: str
    result: Dict[str, Any]

class BatchProcessResponse(BaseModel):
    status: str
    result: Dict[str, Any]

class CredentialsStatusResponse(BaseModel):
    status: str
    credentials: Dict[str, Dict[str, Any]]