import uuid
import json
import logging
import os
from sqlalchemy.orm import Session
from rq import Retry

from yalla_ludo.schema import YallaLoadRequest
from yalla_ludo.service import yalla_pay_recharge
from .database import SessionLocal, init_db
from .models import Transaction
from .schema import TransactionStatusResponse, TransactionIDResponse, TransactionStatus
from .utils import notify_glizer
from .worker import get_queue

# Setup logging
logger = logging.getLogger(__name__)

# Ensure tables are created at import time
init_db()


def _get_db_session() -> Session:
    """Helper to get a transactional DB session."""
    return SessionLocal()


def _get_max_retries() -> int:
    """Get the maximum number of retries from environment variable."""
    return int(os.getenv("MAX_RETRIES", "3"))


def _validate_payload_serialization(payload: dict) -> dict:
    """Validate that payload can be properly serialized/deserialized."""
    try:
        # Test serialization/deserialization
        json_str = json.dumps(payload, ensure_ascii=False)
        validated_payload = json.loads(json_str)
        logger.debug(f"Payload validation successful: {len(json_str)} characters")
        return validated_payload
    except (TypeError, ValueError, UnicodeError) as e:
        logger.error(f"Payload serialization validation failed: {str(e)}")
        raise ValueError(f"Invalid payload for job serialization: {str(e)}")


def cleanup_orphaned_transactions():
    """Clean up any pending transactions that might reference corrupted Redis job data."""
    try:
        
        logger.info("Checking for orphaned pending transactions...")
        
        db = _get_db_session()
        try:
            # Get all pending transactions
            pending_txs = db.query(Transaction).filter(
                Transaction.status == "pending"
            ).all()
            
            if pending_txs:
                logger.warning(f"Found {len(pending_txs)} pending transactions, clearing them due to Redis reset")
                
                # Mark all as error since Redis was cleared
                for tx in pending_txs:
                    tx.status = "error"
                    logger.info(f"Marked transaction {tx.id} as error due to Redis cleanup")
                
                db.commit()
                logger.info(f"Cleaned up {len(pending_txs)} orphaned transactions")
            else:
                logger.info("No orphaned transactions found")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error during transaction cleanup: {str(e)}")


# ---------------------------------------------------------------------------
# RQ Job functions
# ---------------------------------------------------------------------------

def process_yalla_load_job(tx_id: str, order_payload: dict):
    """RQ job function to process Yalla load transaction."""
    try:
        # Validate input parameters
        if not isinstance(tx_id, str) or not isinstance(order_payload, dict):
            raise ValueError(f"Invalid job parameters: tx_id={type(tx_id)}, payload={type(order_payload)}")
        
        logger.info(f"Processing Yalla load transaction {tx_id}")
        
        # Parse the payload as YallaLoadRequest
        yalla_request = YallaLoadRequest(**order_payload)
        
        # Run the YallaPay recharge flow
        succeeded = yalla_pay_recharge(
            amount=yalla_request.amount,
            itemType=yalla_request.itemType,
            playerId=yalla_request.playerId,
            pinCode=yalla_request.pinCode,
        )

        if succeeded:
            update_status(tx_id, "success", notify=True)
            logger.info(f"Transaction {tx_id} completed successfully")
        else:
            # Let RQ handle the retry mechanism
            raise Exception(f"YallaPay recharge failed for transaction {tx_id}")
            
    except Exception as e:
        logger.error(f"Error processing Yalla load transaction {tx_id}: {str(e)}")
        # Mark as error only if this is the final attempt (RQ will handle this automatically)
        raise e


def on_job_failure(job, connection, type, value, traceback):
    """Callback function called when an RQ job fails permanently."""
    tx_id = job.args[0] if job.args else None
    if tx_id:
        logger.error(f"Transaction {tx_id} failed permanently after all retries")
        update_status(tx_id, "error", notify=True)


def process_transaction_by_type_job(tx_id: str, order_type: str, order_payload: dict):
    """RQ job function to process a transaction based on its order type."""
    try:
        if order_type == "yalla_ludo":
            process_yalla_load_job(tx_id, order_payload)
        else:
            logger.error(f"Unknown order type: {order_type} for transaction {tx_id}")
            update_status(tx_id, "error", notify=True)
            raise Exception(f"Unknown order type: {order_type}")
    except Exception as e:
        logger.error(f"Error processing transaction {tx_id}: {str(e)}")
        raise e


# ---------------------------------------------------------------------------
# Public service API
# ---------------------------------------------------------------------------


def clean_payload(payload):
    """Clean payload to ensure it's UTF-8 compatible and JSON serializable"""
    if isinstance(payload, dict):
        return {clean_payload(k): clean_payload(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [clean_payload(item) for item in payload]
    elif isinstance(payload, tuple):
        return tuple(clean_payload(item) for item in payload)
    elif isinstance(payload, str):
        # Ensure string is properly encoded and doesn't contain invalid UTF-8
        try:
            # First, encode as UTF-8 to catch any issues
            encoded = payload.encode('utf-8')
            # Then decode back to ensure it's valid
            return encoded.decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            # If there are encoding issues, replace problematic characters
            return payload.encode('utf-8', errors='replace').decode('utf-8')
    elif isinstance(payload, bytes):
        # Convert bytes to string safely
        try:
            return payload.decode('utf-8')
        except UnicodeDecodeError:
            return payload.decode('utf-8', errors='replace')
    elif isinstance(payload, (int, float, bool)) or payload is None:
        # These types are already JSON-safe
        return payload
    else:
        # For any other type, convert to string safely
        try:
            str_repr = str(payload)
            return clean_payload(str_repr)
        except Exception:
            return "<non-serializable object>"

def create_yalla_transaction(body: YallaLoadRequest) -> TransactionIDResponse:
    """Create a new Yalla transaction and enqueue its processing."""
    tx_id = str(uuid.uuid4())
    
    # Store the order payload as JSON
    order_payload = body.model_dump()
    order_type = "yalla_ludo"
    max_retries = _get_max_retries()

    # Validate payload can be serialized properly
    validated_payload = _validate_payload_serialization(order_payload)

    db = _get_db_session()
    try:
        db.add(Transaction(
            id=tx_id, 
            status="pending",
            order_type=order_type,
            order_payload=json.dumps(validated_payload, ensure_ascii=False)
        ))
        db.commit()
    finally:
        db.close()

    # Enqueue job with RQ with retry configuration
    try:
        queue = get_queue()
        retry = Retry(max=max_retries)
        
        job = queue.enqueue(
            process_yalla_load_job,
            tx_id,
            clean_payload(validated_payload),
            retry=retry,
            on_failure=on_job_failure,
            job_timeout='10m'  # 10 minute timeout per job
        )
        
        logger.info(f"Enqueued transaction {tx_id} as job {job.id} with {max_retries} max retries")
    except Exception as e:
        logger.error(f"Failed to enqueue transaction {tx_id}: {str(e)}")
        # Mark transaction as error if we can't enqueue it
        update_status(tx_id, "error", notify=True)
        raise

    return TransactionIDResponse(transactionsId=tx_id)


def get_status(tx_id: str) -> TransactionStatusResponse:
    db = _get_db_session()
    try:
        tx = db.query(Transaction).get(tx_id)
        if not tx:
            raise KeyError("Unknown transaction id")
        return TransactionStatusResponse(status=tx.status)
    finally:
        db.close()


def update_status(tx_id: str, status: TransactionStatus, notify: bool = False):
    db = _get_db_session()
    try:
        tx = db.query(Transaction).get(tx_id)
        if not tx:
            tx = Transaction(id=tx_id, status=status)
            db.add(tx)
        else:
            tx.status = status
        db.commit()
    finally:
        db.close()

    if notify:
        notify_glizer(tx_id, status)


def get_pending_transactions():
    """Get all pending transactions from the database."""
    db = _get_db_session()
    try:
        pending_txs = db.query(Transaction).filter(
            Transaction.status == "pending"
        ).all()
        return pending_txs
    finally:
        db.close()


def resume_pending_transactions():
    """Resume all pending transactions found in the database."""
    pending_txs = get_pending_transactions()
    
    logger.info(f"Found {len(pending_txs)} pending transactions to resume")
    
    queue = get_queue()
    max_retries = _get_max_retries()
    
    for tx in pending_txs:
        try:
            if tx.order_payload:
                order_payload = json.loads(tx.order_payload)
                
                # Validate payload can be serialized properly
                validated_payload = _validate_payload_serialization(order_payload)
                
                logger.info(f"Resuming transaction {tx.id} of type {tx.order_type}")
                
                # Enqueue with max retries from environment
                retry = Retry(max=max_retries)
                
                job = queue.enqueue(
                    process_transaction_by_type_job,
                    tx.id,
                    tx.order_type,
                    clean_payload(validated_payload),
                    retry=retry,
                    on_failure=on_job_failure,
                    job_timeout='10m'
                )
                
                logger.info(f"Re-enqueued transaction {tx.id} as job {job.id} with {max_retries} max retries")
            else:
                logger.warning(f"Transaction {tx.id} has no order payload, marking as error")
                update_status(tx.id, "error", notify=True)
        except Exception as e:
            logger.error(f"Error resuming transaction {tx.id}: {str(e)}")
            update_status(tx.id, "error", notify=True)