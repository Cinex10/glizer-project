from fastapi import APIRouter, Header, HTTPException

from pubg.schema import PubgLoadRequest

from .schema import TransactionIDResponse, TransactionStatusResponse
from .utils import check_bot_token
from . import service

router = APIRouter(prefix="/transaction")


@router.post("/create", response_model=TransactionIDResponse)
async def create_transaction(
    pubg_body: PubgLoadRequest,
    token: str = Header(...),
):
    """Create a new transaction. Currently supports only Yalla load."""
    check_bot_token(token)

    return service.create_pubg_transaction(pubg_body)


@router.get("/{transaction_id}", response_model=TransactionStatusResponse)
async def get_transaction_status(transaction_id: str, token: str = Header(...)):
    check_bot_token(token)
    try:
        return service.get_status(transaction_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown transaction id")