"""
Main FastAPI application - adapté pour PostgreSQL et tous les bots (1-10)
"""
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
import logging
from typing import List, Optional
import os
from dotenv import load_dotenv
import json

from database.postgresql import get_postgres_session, close_postgres_connection
from database.models import BotTransaction
from schemas import (
    BotTransactionResponse, 
    BotTransactionStatusResponse, 
    BotTransactionListItem,
    HealthResponse,
    BotStatsResponse
)
from thread_manager import ThreadManager
from services.transaction_processor import TransactionProcessor
from logging_config import get_logger

# Configuration
load_dotenv()
logger = get_logger(__name__)

# Thread manager global
thread_manager = None
transaction_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global thread_manager, transaction_processor
    logger.info("Starting Glizer Bot Processor v2.0 for PostgreSQL...")
    
    # Test de connexion PostgreSQL
    try:
        from sqlalchemy import text
        logger.info("Testing PostgreSQL connection...")
        db = get_postgres_session()
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.fetchone()
        db.close()
        logger.info("PostgreSQL connection test successful")
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        raise Exception(f"Cannot start without database connection: {e}")
    
    # Créer les dossiers nécessaires
    try:
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        os.makedirs(screenshots_dir, mode=0o755, exist_ok=True)
        logger.info(f"Screenshots directory ensured: {screenshots_dir}")
        
        config_dir = os.path.join(os.getcwd(), 'config')
        os.makedirs(config_dir, mode=0o755, exist_ok=True)
        logger.info(f"Config directory ensured: {config_dir}")
    except Exception as e:
        logger.warning(f"Could not create directories: {e}")
    
    # Initialize transaction processor
    transaction_processor = TransactionProcessor()
    logger.info("Transaction processor initialized")
    
    # Start thread manager (10 workers for all bots 1-10)
    thread_manager = ThreadManager(max_workers=10)
    thread_manager.start()
    logger.info("Thread manager started successfully with 10 workers")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Glizer Bot Processor...")
    if thread_manager:
        logger.info("Stopping thread manager...")
        thread_manager.stop()
        logger.info("Thread manager stopped successfully")
    
    # Close PostgreSQL connection
    close_postgres_connection()
    logger.info("PostgreSQL connection closed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Glizer Bot Processor API",
    description="Automated PUBG UC recharge system for all bots (1-10)",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Glizer Bot Processor API v2.0",
        "description": "Automated PUBG UC recharge system for all bots (1-10)",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de santé du système"""
    
    status = thread_manager.get_status()
    
    return HealthResponse(
        status="healthy" if status["running"] else "stopped",
        active_threads=status["active_threads"],
        max_workers=status["max_workers"],
        thread_names=status["thread_names"]
    )

@app.get("/stats")
async def get_stats():
    """Obtenir les statistiques complètes avec rotation des credentials"""
    
    try:
        system_stats = transaction_processor.get_system_stats()
        thread_status = thread_manager.get_status()
        
        return {
            "system_status": "running",
            "bots": system_stats.get("all_bots", {}),
            "totals": {
                "pending": system_stats.get("total_pending", 0),
                "processing": system_stats.get("total_processing", 0),
                "success": system_stats.get("total_success", 0),
                "failed": system_stats.get("total_failed", 0)
            },
            "credential_rotation": system_stats.get("credential_rotation", {}),
            "thread_manager": {
                "running": thread_status.get("running", False),
                "active_threads": thread_status.get("active_threads", 0),
                "available_workers": thread_status.get("available_workers", 0),
                "queue_size": thread_status.get("queue_size", 0),
                "thread_names": thread_status.get("thread_names", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.get("/bot/{bot_num}/stats", response_model=BotStatsResponse)
async def get_bot_stats(bot_num: int):
    """Obtenir les statistiques d'un bot spécifique"""
    
    if bot_num not in list(range(1, 11)):  # bots 1 à 10
        raise HTTPException(status_code=400, detail="Bot number must be between 1 and 10")
    
    try:
        stats = transaction_processor.poller.get_bot_stats(bot_num)
        return BotStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting stats for bot {bot_num}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats for bot {bot_num}")

@app.get("/transactions", response_model=List[BotTransactionListItem])
async def list_transactions(
    bot_num: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Lister les transactions de tous les bots (1-10)"""
    
    db = get_postgres_session()
    try:
        query = db.query(BotTransaction).filter(
            BotTransaction.bot_num.in_(list(range(1, 11))),  # bots 1 à 10
            BotTransaction.bot_type == "pubg"
        )
        
        # Filtres optionnels
        if bot_num is not None:
            if bot_num not in list(range(1, 11)):  # bots 1 à 10
                raise HTTPException(status_code=400, detail="Bot number must be between 1 and 10")
            query = query.filter(BotTransaction.bot_num == bot_num)
        
        if status is not None:
            query = query.filter(BotTransaction.status == status)
        
        transactions = query.order_by(
            BotTransaction.id.desc()
        ).limit(limit).all()
        
        return [
            BotTransactionListItem(
                id=t.id,
                bot_num=t.bot_num,
                status=t.status,
                created_at=None,  # Colonne supprimée
                updated_at=None,  # Colonne supprimée
                retry_count=0,    # Colonne supprimée
                player_id=t.get_player_id()
            )
            for t in transactions
        ]
        
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list transactions")
    finally:
        db.close()

@app.get("/transaction/{transaction_id}", response_model=BotTransactionStatusResponse)
async def get_transaction_status(transaction_id: str):
    """Récupérer le statut d'une transaction"""
    
    db = get_postgres_session()
    try:
        transaction = db.query(BotTransaction).filter(
            BotTransaction.id == transaction_id,
            BotTransaction.bot_num.in_(list(range(1, 11)))  # bots 1 à 10
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Parser le résultat si disponible
        result = None
        if transaction.payload and isinstance(transaction.payload, dict):
            result = transaction.payload.get('result')
        
        return BotTransactionStatusResponse(
            transaction_id=transaction.id,
            bot_num=transaction.bot_num,
            status=transaction.status,
            created_at=transaction.created_at,
            started_at=transaction.started_at,
            completed_at=transaction.completed_at,
            retry_count=transaction.retry_count,
            max_retries=transaction.max_retries,
            result=result,
            error_message=transaction.error_message,
            player_id=transaction.get_player_id(),
            redeem_codes=transaction.get_redeem_codes()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transaction status")
    finally:
        db.close()

@app.post("/transaction/{transaction_id}/process")
async def process_transaction(transaction_id: str):
    """Traiter une transaction spécifique manuellement"""
    
    try:
        result = thread_manager.process_single_transaction(transaction_id)
        return {
            "transaction_id": transaction_id,
            "status": "processed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process transaction: {str(e)}")

@app.post("/process/pending")
async def process_pending_transactions():
    """Traiter toutes les transactions en attente"""
    
    try:
        result = thread_manager.force_process_pending()
        return {
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing pending transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process pending transactions: {str(e)}")

@app.get("/credentials/status")
async def check_credentials_status():
    """Vérifier le statut des credentials et de la rotation"""
    
    try:
        credential_stats = thread_manager.get_credential_stats()
        
        return {
            "status": "ok",
            "rotation_status": {
                "current_position": credential_stats.get("current_position", 0),
                "total_credentials": credential_stats["total_credentials"],
                "rotation_progress": credential_stats.get("rotation_progress", 0),
                "next_credential": {
                    "index": credential_stats.get("current_position", 0),
                    "email": credential_stats["usage_stats"].get(str(credential_stats.get("current_position", 0)), {}).get("email", "unknown")
                }
            },
            "usage_stats": credential_stats["usage_stats"],
            "email_status": {
                "active_emails": credential_stats.get("active_emails", []),
                "active_emails_count": credential_stats.get("active_emails_count", 0),
                "available_emails": credential_stats.get("available_emails", []),
                "available_emails_count": credential_stats.get("available_emails_count", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking credentials: {e}")
        raise HTTPException(status_code=500, detail="Failed to check credentials")

@app.post("/credentials/rotate")
async def force_credential_rotation():
    """Forcer la rotation vers le prochain credential"""
    
    try:
        credential, index = thread_manager.force_next_credential()
        
        return {
            "status": "rotated",
            "message": "Credential rotation forced",
            "next_credential": {
                "id": credential.get("id", index),
                "email": credential["email"],
                "index": index
            }
        }
        
    except Exception as e:
        logger.error(f"Error forcing credential rotation: {e}")
        raise HTTPException(status_code=500, detail="Failed to force credential rotation")

@app.post("/credentials/reset")
async def reset_credential_rotation(index: int = 0):
    """Réinitialiser la rotation des credentials"""
    
    try:
        thread_manager.reset_credential_rotation(index)
        
        return {
            "status": "reset",
            "message": f"Credential rotation reset to index {index}",
            "current_position": index
        }
        
    except Exception as e:
        logger.error(f"Error resetting credential rotation: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset credential rotation")

@app.get("/queue/status")
async def get_queue_status():
    """Obtenir le statut de la queue de traitement"""
    
    try:
        queue_status = thread_manager.get_queue_status()
        
        return {
            "status": "ok",
            "queue_info": queue_status
        }
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get queue status")

@app.post("/queue/clear-processing")
async def clear_processing_tracking():
    """Nettoyer manuellement le tracking des transactions en cours (pour maintenance)"""
    
    try:
        result = thread_manager.clear_processing_tracking()
        
        return {
            "status": "ok",
            "message": f"Cleared {result['cleared_count']} transactions from processing tracking",
            "cleared_transaction_ids": result['cleared_transaction_ids']
        }
        
    except Exception as e:
        logger.error(f"Error clearing processing tracking: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear processing tracking")

@app.get("/queue/processing/{transaction_id}")
async def check_transaction_processing(transaction_id: str):
    """Vérifier si une transaction est en cours de traitement"""
    
    try:
        is_processing = thread_manager.is_transaction_processing(transaction_id)
        
        return {
            "status": "ok",
            "transaction_id": transaction_id,
            "is_processing": is_processing
        }
        
    except Exception as e:
        logger.error(f"Error checking transaction processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check transaction processing status")

@app.get("/emails/status")
async def get_email_status():
    """Obtenir le statut des emails (actifs, disponibles)"""
    
    try:
        email_status = thread_manager.get_email_status()
        
        return {
            "status": "ok",
            "email_status": {
                "active_emails": list(email_status["active_emails"]),
                "available_emails": email_status["available_emails"],
                "total_credentials": email_status["total_credentials"],
                "active_count": email_status["active_count"],
                "available_count": email_status["available_count"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting email status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get email status")

@app.post("/emails/release-all")
async def force_release_all_emails():
    """Forcer la libération de tous les emails actifs (pour maintenance)"""
    
    try:
        result = thread_manager.force_release_all_emails()
        
        return {
            "status": "ok",
            "message": f"Released {result['released_count']} emails",
            "released_emails": result["released_emails"],
            "released_count": result["released_count"]
        }
        
    except Exception as e:
        logger.error(f"Error releasing emails: {e}")
        raise HTTPException(status_code=500, detail="Failed to release emails")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)