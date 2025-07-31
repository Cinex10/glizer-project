from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Any, Dict
from src.transaction.schema import GlizerWebhookPayload

app = FastAPI()

@app.post("/webhook")
async def receive_webhook(
    payload: GlizerWebhookPayload,
    authorization: str = Header(None)
):
    """Simple webhook endpoint to receive and process webhook notifications."""
    
    # Basic authentication check (optional)
    # if authorization and not authorization.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # Log the received webhook
    print(f"Received webhook - Event: {payload.event}, Data: {payload.model_dump_json()}")
    
    # Process the webhook based on event type
    if payload.event == "ON_TRANSACTION_STATUS_CHANGED":
        # Handle transaction update
        transaction_id = payload.transactionsId
        status = payload.status
        print(f"Transaction {transaction_id} updated to status: {status}")
    
    return {"status": "received", "message": "Webhook processed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
