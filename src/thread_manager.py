"""
Thread Manager avec rotation des credentials et queue intelligente
"""
import threading
import time
import json
import logging
from datetime import datetime
from typing import List, Optional, Set
from queue import Queue, Empty
from database.postgresql import get_postgres_engine
from database.models import BotTransaction
from services.transaction_processor import TransactionProcessor
from services.credential_manager import CredentialManager
from logging_config import get_logger

logger = get_logger(__name__)

class ThreadManager:
    def __init__(self, max_workers: int = 10):
        """
        Initialiser le gestionnaire de threads avec rotation des credentials
        
        Args:
            max_workers: Nombre maximum de workers (défaut: 10)
        """
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self.engine = get_postgres_engine()
        self.processor = TransactionProcessor()
        self.credential_manager = CredentialManager()
        
        # Queue intelligente pour les transactions
        self.transaction_queue = Queue()
        self.worker_availability = [True] * max_workers  # Track worker availability
        self.worker_locks = [threading.Lock() for _ in range(max_workers)]
        
        # Système de tracking pour éviter les bots multiples sur la même transaction
        self.processing_transactions: Set[str] = set()  # IDs des transactions en cours
        self.processing_lock = threading.Lock()  # Lock pour la thread safety
        
        logger.info(f"ThreadManager initialized with {max_workers} workers and credential rotation")
    
    def start(self):
        """Démarrer les workers avec rotation des credentials"""
        self.running = True
        
        # Créer des workers génériques (pas de bot_num spécifique)
        for worker_id in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                args=(worker_id,),
                daemon=True,
                name=f"CredentialWorker-{worker_id}"
            )
            worker.start()
            self.workers.append(worker)
            logger.info(f"Worker {worker_id} started for credential rotation")
        
        # Démarrer le thread de polling des transactions
        poller_thread = threading.Thread(
            target=self._transaction_poller,
            daemon=True,
            name="TransactionPoller"
        )
        poller_thread.start()
        self.workers.append(poller_thread)
        
        logger.info("All workers started with credential rotation system")
    
    def _transaction_poller(self):
        """Thread de polling pour récupérer les transactions de la base"""
        logger.info("Transaction poller started")
        
        while self.running:
            try:
                # Récupérer les transactions en attente
                pending_transactions = self._get_pending_transactions()
                
                if pending_transactions:
                    # Filtrer les transactions déjà en cours de traitement
                    new_transactions = []
                    with self.processing_lock:
                        for transaction in pending_transactions:
                            if transaction.id not in self.processing_transactions:
                                new_transactions.append(transaction)
                                self.processing_transactions.add(transaction.id)
                                logger.info(f"Added transaction {transaction.id} to processing queue")
                            else:
                                logger.debug(f"Transaction {transaction.id} already being processed, skipping")
                    
                    if new_transactions:
                        logger.info(f"Found {len(new_transactions)} new pending transactions (filtered from {len(pending_transactions)} total)")
                        
                        # Ajouter les nouvelles transactions à la queue
                        for transaction in new_transactions:
                            self.transaction_queue.put(transaction)
                    else:
                        logger.debug(f"All {len(pending_transactions)} pending transactions are already being processed")
                
                # Attendre avant le prochain poll
                time.sleep(5)  # Polling toutes les 5 secondes
                
            except Exception as e:
                logger.error(f"Error in transaction poller: {e}")
                time.sleep(10)  # Attendre en cas d'erreur
    
    def _worker(self, worker_id: int):
        """
        Boucle principale du worker avec rotation des credentials
        
        Args:
            worker_id: ID du worker (0 ou 1)
        """
        worker_name = f"CredentialWorker-{worker_id}"
        logger.info(f"{worker_name} started - ready for credential rotation")
        
        while self.running:
            try:
                # Marquer le worker comme disponible
                with self.worker_locks[worker_id]:
                    self.worker_availability[worker_id] = True
                
                # Attendre une transaction de la queue
                try:
                    transaction = self.transaction_queue.get(timeout=5)  # Timeout de 5 secondes
                except Empty:
                    continue  # Pas de transaction, continuer la boucle
                
                # Marquer le worker comme occupé
                with self.worker_locks[worker_id]:
                    self.worker_availability[worker_id] = False
                
                logger.info(f"{worker_name}: Processing transaction {transaction.id}")
                
                try:
                    # Traiter la transaction avec rotation des credentials
                    result = self.processor.process_transaction(transaction)
                    
                    logger.info(f"{worker_name}: Transaction {transaction.id} processed with status: {result['status']}")
                    
                    # Log du credential utilisé si disponible
                    if 'credential_used' in result:
                        cred_info = result['credential_used']
                        logger.info(f"{worker_name}: Used credential {cred_info['id']} ({cred_info['email']})")
                    
                except Exception as e:
                    logger.error(f"{worker_name}: Error processing transaction {transaction.id}: {e}")
                
                finally:
                    # Nettoyer le tracking - retirer la transaction de la liste des transactions en cours
                    with self.processing_lock:
                        self.processing_transactions.discard(transaction.id)
                        logger.info(f"{worker_name}: Removed transaction {transaction.id} from processing tracking")
                    
                    # Marquer la tâche comme terminée
                    self.transaction_queue.task_done()
                
            except Exception as e:
                logger.error(f"{worker_name}: Worker error: {str(e)}")
                time.sleep(5)  # Attendre avant de continuer en cas d'erreur
    
    def _get_pending_transactions(self) -> List[BotTransaction]:
        """Récupérer les transactions en attente depuis PostgreSQL"""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=self.engine)
        session = SessionLocal()
        
        try:
            transactions = session.query(BotTransaction).filter(
                BotTransaction.bot_num.in_(list(range(1, 11))),  # bots 1 à 10
                BotTransaction.bot == "pubg",
                BotTransaction.status == "pending"
            ).order_by(BotTransaction.id.asc()).all()
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error fetching pending transactions: {e}")
            return []
        finally:
            session.close()
    
    def stop(self):
        """Arrêter tous les workers"""
        logger.info("Stopping all workers...")
        self.running = False
        
        # Attendre que tous les workers se terminent
        for worker in self.workers:
            worker.join(timeout=10)
        
        self.workers.clear()
        logger.info("All workers stopped successfully")
    
    def get_status(self):
        """Retourner le statut du gestionnaire et des workers"""
        try:
            # Obtenir les statistiques du système
            system_stats = self.processor.get_system_stats()
            
            # Calculer les workers actifs et disponibles
            active_workers = sum(1 for worker in self.workers if worker.is_alive())
            available_workers = sum(1 for available in self.worker_availability if available)
            
            # Statistiques de la queue
            queue_size = self.transaction_queue.qsize()
            
            # Statistiques du tracking des transactions en cours
            with self.processing_lock:
                processing_count = len(self.processing_transactions)
                processing_ids = list(self.processing_transactions)
            
            return {
                "running": self.running,
                "active_threads": active_workers,
                "max_workers": self.max_workers,
                "available_workers": available_workers,
                "thread_names": [worker.name for worker in self.workers if worker.is_alive()],
                "queue_size": queue_size,
                "processing_transactions_count": processing_count,
                "processing_transactions_ids": processing_ids,
                "all_bots": system_stats.get("all_bots", {}),
                "total_pending": system_stats.get("total_pending", 0),
                "total_processing": system_stats.get("total_processing", 0),
                "total_success": system_stats.get("total_success", 0),
                "total_failed": system_stats.get("total_failed", 0),
                "credential_rotation": system_stats.get("credential_rotation", {})
            }
            
        except Exception as e:
            logger.error(f"Error getting thread manager status: {e}")
            return {
                "running": self.running,
                "active_threads": 0,
                "max_workers": self.max_workers,
                "available_workers": 0,
                "thread_names": [],
                "queue_size": 0,
                "error": str(e)
            }
    
    def process_single_transaction(self, transaction_id: str):
        """
        Traiter une transaction spécifique (pour usage API)
        
        Args:
            transaction_id: ID de la transaction à traiter
        """
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=self.engine)
        session = SessionLocal()
        
        try:
            # Récupérer la transaction
            transaction = session.query(BotTransaction).filter(
                BotTransaction.id == transaction_id
            ).first()
            
            if not transaction:
                raise Exception(f"Transaction {transaction_id} not found")
            
            if not transaction.is_pubg_bot():
                raise Exception(f"Transaction {transaction_id} is not a PUBG bot transaction")
            
            # Traiter la transaction avec rotation des credentials
            result = self.processor.process_transaction(transaction)
            return result
            
        except Exception as e:
            logger.error(f"Error processing single transaction {transaction_id}: {e}")
            raise
        finally:
            session.close()
    
    def force_process_pending(self):
        """
        Forcer le traitement de toutes les transactions en attente
        (pour usage API ou maintenance)
        """
        logger.info("Force processing all pending transactions")
        return self.processor.process_pending_transactions()
    
    def get_credential_stats(self):
        """Obtenir les statistiques des credentials"""
        return self.credential_manager.get_usage_stats()
    
    def get_email_status(self):
        """Obtenir le statut des emails (actifs, disponibles)"""
        return self.processor.get_email_status()
    
    def force_release_all_emails(self):
        """Forcer la libération de tous les emails actifs"""
        return self.processor.force_release_all_emails()
    
    def reset_credential_rotation(self, index: int = 0):
        """Réinitialiser la rotation des credentials"""
        self.credential_manager.reset_rotation(index)
        logger.info(f"Credential rotation reset to index {index}")
    
    def force_next_credential(self):
        """Forcer l'utilisation du prochain credential"""
        return self.credential_manager.force_next_credential()
    
    def get_queue_status(self):
        """Obtenir le statut de la queue"""
        with self.processing_lock:
            processing_transactions = list(self.processing_transactions)
        
        return {
            "queue_size": self.transaction_queue.qsize(),
            "available_workers": sum(1 for available in self.worker_availability if available),
            "processing_transactions": processing_transactions,
            "processing_count": len(processing_transactions),
            "worker_status": [
                {
                    "worker_id": i,
                    "available": self.worker_availability[i],
                    "name": f"CredentialWorker-{i}"
                }
                for i in range(self.max_workers)
            ]
        }
    
    def clear_processing_tracking(self):
        """Nettoyer manuellement le tracking des transactions en cours (pour maintenance)"""
        with self.processing_lock:
            cleared_count = len(self.processing_transactions)
            cleared_ids = list(self.processing_transactions)
            self.processing_transactions.clear()
        
        logger.info(f"Cleared processing tracking: {cleared_count} transactions ({cleared_ids})")
        return {
            "cleared_count": cleared_count,
            "cleared_transaction_ids": cleared_ids
        }
    
    def is_transaction_processing(self, transaction_id: str) -> bool:
        """Vérifier si une transaction est en cours de traitement"""
        with self.processing_lock:
            return transaction_id in self.processing_transactions