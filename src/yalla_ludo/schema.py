from pydantic import BaseModel, Field
from typing import Literal



class YallaLoadRequest(BaseModel):
    """Payload for a Yalla load transaction request."""

    itemType: Literal["diamonds", "golds"]
    amount: int = Field(..., gt=0)
    pinCode: str
    playerId: str