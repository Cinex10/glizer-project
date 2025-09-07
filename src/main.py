from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
# HTTPBearer supprimé - plus d'authentification
import logging
from typing import List, Optional
import os
from dotenv import load_dotenv
import json

from database import get_db, init_db, get_db_session
from models import Transaction
from schemas import (
    PubgRequest, 
    TransactionResponse, 
    TransactionStatusResponse, 
    TransactionListItem,
    HealthResponse
)
from thread_manager import ThreadManager
from logging_config import get_logger

# Configuration
load_dotenv()
logger = get_logger(__name__)

# Thread manager global
thread_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global thread_manager
    logger.info("Starting PUBG Recharge Bot v2.0...")
    
    # Initialize database
    init_db()
    
    # Start thread manager (single worker with FIFO processing)
    thread_manager = ThreadManager(max_workers=1)
    thread_manager.start()
    logger.info("Thread manager started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PUBG Recharge Bot...")
    if thread_manager:
        logger.info("Stopping thread manager...")
        thread_manager.stop()
        logger.info("Thread manager stopped successfully")

# Create FastAPI app with lifespan
app = FastAPI(
    title="PUBG Recharge Bot API",
    description="Automated PUBG UC recharge system",
    version="2.0.0",
    lifespan=lifespan
)

# Authentification supprimée - API publique

@app.post("/transaction/create", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: PubgRequest,
    db = Depends(get_db)
):
    
    try:
        # Create transaction object
        transaction = Transaction(
            email=transaction_data.email,
            password=transaction_data.password,
            player_id=transaction_data.player_id,
            redeem_codes=json.dumps(transaction_data.redeem_codes),
            status="pending"
        )
        
        # Save to database
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Created transaction {transaction.id} for email {transaction.email}")
        
        # Add to processing queue using transaction ID
        if thread_manager:
            thread_manager.add_task(transaction.id)
        
        return TransactionResponse(
            transaction_id=transaction.id,
            status="pending",
            message="Transaction created and queued for processing"
        )
        
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create transaction")
    finally:
        db.close()

@app.get("/transaction/{transaction_id}", response_model=TransactionStatusResponse)
async def get_transaction_status(
    transaction_id: str
):
    """Récupérer le statut d'une transaction"""
    
    db = get_db_session()
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Parser le résultat si disponible
        result = None
        if transaction.result:
            try:
                result = json.loads(transaction.result)
            except:
                result = {"raw_result": transaction.result}
        
        return TransactionStatusResponse(
            transaction_id=transaction.id,
            status=transaction.status,
            created_at=transaction.created_at,
            started_at=transaction.started_at,
            completed_at=transaction.completed_at,
            retry_count=transaction.retry_count,
            max_retries=transaction.max_retries,
            result=result,
            error_message=transaction.error_message
        )
        
    finally:
        db.close()

@app.get("/transactions", response_model=list[TransactionListItem])
async def list_transactions(
    limit: int = 50
):
    """Lister les transactions récentes"""
    
    db = get_db_session()
    try:
        transactions = db.query(Transaction).order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()
        
        return [
            TransactionListItem(
                id=t.id,
                email=t.email,
                player_id=t.player_id,
                status=t.status,
                created_at=t.created_at,
                retry_count=t.retry_count
            )
            for t in transactions
        ]
        
    finally:
        db.close()

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
    """Obtenir les statistiques essentielles du système"""
    
    db = get_db_session()
    try:
        # Compter les transactions par statut essentiel
        pending = db.query(Transaction).filter(Transaction.status == "pending").count()
        processing = db.query(Transaction).filter(Transaction.status == "processing").count()
        success = db.query(Transaction).filter(Transaction.status == "success").count()
        failed = db.query(Transaction).filter(Transaction.status == "failed").count()
        
        # Statistiques générales
        total_transactions = pending + processing + success + failed
        success_rate = (success / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            "total_transactions": total_transactions,
            "success_rate": round(success_rate, 2),
            "status_breakdown": {
                "pending": pending,      # En attente
                "processing": processing, # En cours d'exécution
                "success": success,      # Réussies
                "failed": failed         # Échouées après 3 tentatives
            },
            "thread_manager": thread_manager.get_status()
        }
        
    finally:
        db.close()

@app.post("/reset-database")
async def reset_database():
    """Réinitialiser complètement la base de données"""
    
    db = get_db_session()
    try:
        # Compter les transactions avant suppression
        total_before = db.query(Transaction).count()
        
        # Supprimer toutes les transactions
        db.query(Transaction).delete()
        db.commit()
        
        logger.info(f"Database reset: {total_before} transactions deleted")
        
        return {
            "message": "Base de données réinitialisée avec succès",
            "deleted_transactions": total_before,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reset database")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
