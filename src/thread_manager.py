import threading
import time
import json
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database import engine, get_db_session
from models import Transaction
from pubg_automation import process_pubg_transaction
from logging_config import get_logger

logger = get_logger(__name__)

class ThreadManager:
    def __init__(self, max_workers: int = 1):  # Un seul worker
        self.max_workers = 1  # Forcer à 1
        self.worker = None
        self.running = False
        self.session_factory = sessionmaker(bind=engine)
        
    def start(self):
        """Démarrer le worker unique"""
        self.running = True
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()
        logger.info("Single worker started with FIFO processing")
    
    def _worker(self):
        """Boucle principale du worker unique - Logique FIFO stricte"""
        logger.info("Worker started - FIFO processing mode")
        
        while self.running:
            try:
                # Récupérer la prochaine transaction à traiter (FIFO strict)
                transaction = self._get_next_transaction()
                
                if not transaction:
                    # Aucune transaction à traiter, attendre un peu
                    time.sleep(2)
                    continue
                
                logger.info(f"Processing transaction {transaction.id} (retry {transaction.retry_count})")
                
                # Marquer comme en cours de traitement
                self._update_transaction_status(
                    transaction.id, 
                    "processing", 
                    started_at=datetime.utcnow()
                )
                
                # Traiter la transaction
                result = process_pubg_transaction(
                    email=transaction.email,
                    password=transaction.password,
                    player_id=transaction.player_id,
                    redeem_codes=json.loads(transaction.redeem_codes) if transaction.redeem_codes else []
                )
                
                # Vérifier le résultat
                if not result:
                    # Aucun résultat - échec complet
                    all_success = False
                    success_count = 0
                    total_codes = 0
                else:
                    success_count = sum(1 for v in result.values() if v == True)
                    total_codes = len(result)
                    all_success = success_count == total_codes
                
                if all_success:
                    # Succès complet - marquer comme terminé
                    self._update_transaction_status(
                        transaction.id,
                        "success",
                        result=json.dumps(result, ensure_ascii=False),
                        completed_at=datetime.utcnow()
                    )
                    logger.info(f"Transaction {transaction.id} completed successfully ({success_count}/{total_codes} codes)")
                elif success_count > 0:
                    # Succès partiel - marquer comme succès partiel
                    self._update_transaction_status(
                        transaction.id,
                        "success",
                        result=json.dumps(result, ensure_ascii=False),
                        completed_at=datetime.utcnow(),
                        error_message=f"Partial success: {success_count}/{total_codes} codes redeemed"
                    )
                    logger.info(f"Transaction {transaction.id} completed with partial success ({success_count}/{total_codes} codes)")
                else:
                    # Échec - décider si retry ou failed
                    new_retry_count = transaction.retry_count + 1
                    
                    if new_retry_count < transaction.max_retries:
                        # Retry - remettre en queue
                        self._update_transaction_status(
                            transaction.id,
                            "pending",  # Remettre en pending pour retry
                            retry_count=new_retry_count,
                            error_message=f"Attempt {new_retry_count} failed: {result}"
                        )
                        logger.warning(f"Transaction {transaction.id} failed, retrying ({new_retry_count}/{transaction.max_retries})")
                    else:
                        # Max retries atteint - marquer comme failed
                        self._update_transaction_status(
                            transaction.id,
                            "failed",
                            result=json.dumps(result, ensure_ascii=False),
                            completed_at=datetime.utcnow(),
                            error_message=f"Failed after {transaction.max_retries} attempts: {result}"
                        )
                        logger.error(f"Transaction {transaction.id} failed permanently after {transaction.max_retries} attempts")
                
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                # En cas d'erreur critique, attendre avant de continuer
                time.sleep(5)
    
    def _get_next_transaction(self):
        """Récupérer la prochaine transaction à traiter (FIFO strict)"""
        session = self.session_factory()
        try:
            # Récupérer la transaction la plus ancienne en attente
            transaction = session.query(Transaction).filter(
                Transaction.status == "pending"
            ).order_by(Transaction.created_at.asc()).first()
            
            return transaction
        except Exception as e:
            logger.error(f"Error getting next transaction: {e}")
            return None
        finally:
            session.close()
    
    def _update_transaction_status(self, transaction_id, status, result=None, error_message=None, completed_at=None, started_at=None, retry_count=None):
        """Mettre à jour le statut d'une transaction"""
        session = self.session_factory()
        try:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
            if transaction:
                transaction.status = status
                if result is not None:
                    transaction.result = result
                if error_message is not None:
                    transaction.error_message = error_message
                if completed_at is not None:
                    transaction.completed_at = completed_at
                if started_at is not None:
                    transaction.started_at = started_at
                if retry_count is not None:
                    transaction.retry_count = retry_count
                
                session.commit()
            else:
                logger.error(f"Transaction {transaction_id} not found for update")
        except Exception as e:
            logger.error(f"Failed to update transaction {transaction_id}: {e}")
            session.rollback()
        finally:
            session.close()
    
    def add_task(self, transaction_id: str):
        """Ajouter une transaction (pour compatibilité avec l'API)"""
        # Pas besoin de queue - le worker récupère directement depuis la DB
        logger.info(f"Transaction {transaction_id} added - will be processed in FIFO order")
    
    def stop(self):
        """Arrêter le worker"""
        self.running = False
        if self.worker:
            self.worker.join(timeout=10)
        logger.info("Worker stopped")
    
    def get_status(self):
        """Retourner le statut du gestionnaire"""
        session = self.session_factory()
        try:
            # Compter les transactions par statut
            pending_count = session.query(Transaction).filter(Transaction.status == "pending").count()
            processing_count = session.query(Transaction).filter(Transaction.status == "processing").count()
            
            return {
                "running": self.running,
                "active_threads": 1 if self.running and self.worker and self.worker.is_alive() else 0,
                "max_workers": 1,
                "thread_names": ["Worker-1"] if self.running and self.worker and self.worker.is_alive() else [],
                "pending_transactions": pending_count,
                "processing_transactions": processing_count
            }
        finally:
            session.close()