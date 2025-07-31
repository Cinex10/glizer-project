import os
import requests
from fastapi import HTTPException

# Tokens/URLs configurable via environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "123456789")
GLIZER_TOKEN = os.getenv("GLIZER_TOKEN", "123456789")
GLIZER_WEBHOOK_URL = os.getenv("GLIZER_WEBHOOK_URL", "http://localhost:8001/webhook")


def check_bot_token(token: str):
    """Validate the token provided by clients calling the bot API."""
    if token != BOT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bot token")


def check_glizer_token(token: str):
    """Validate the token provided by Glizer webhooks."""
    if token != GLIZER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Glizer token")


def notify_glizer(transaction_id: str, status: str):
    """Send a status change notification to Glizer webhook."""
    payload = {
        "event": "ON_TRANSACTION_STATUS_CHANGED",
        "transactionsId": transaction_id,
        "status": status,
    }
    headers = {
        "token": GLIZER_TOKEN,
        "Content-Type": "application/json",
    }
    try:
        requests.post(GLIZER_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
    except requests.RequestException as exc:
        # Log the error; in production use proper logging
        print(f"Failed to notify Glizer: {exc}")