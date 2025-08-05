from pydantic import BaseModel, Field
from typing import Literal



class PubgLoadRequest(BaseModel):
    """Payload for a PUBG load transaction request."""

    email: str
    password: str
    playerId: str
    redeemCodes: list[str]