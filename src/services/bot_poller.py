"""
Service de polling pour surveiller les transactions de tous les bots (1-10)
"""
import time
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import sessionmaker
from database.postgresql import get_postgres_engine, get_postgres_session
from database.models import BotTransaction
from logging_config import get_logger

logger = get_logger(__name__)

class BotPoller:
    def __init__(self, poll_interval: int = 30):
        """
        Initialiser le poller
        
        Args:
            poll_interval: Intervalle de polling en secondes (défaut: 30)
        """
        self.poll_interval = poll_interval
        self.running = False
        self.engine = get_postgres_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"BotPoller initialized with {poll_interval}s interval")
    
    def get_pending_transactions(self) -> List[BotTransaction]:
        """
        Récupérer les transactions en attente pour tous les bots (1-10)
        Ne récupère que les transactions "pending" (plus de "processing")
        
        Returns:
            Liste des transactions PUBG en attente
        """
        session = self.SessionLocal()
        try:
            # Récupérer les transactions PUBG de tous les bots (1-10) en attente uniquement
            transactions = session.query(BotTransaction).filter(
                BotTransaction.bot_num.in_(list(range(1, 11))),  # bots 1 à 10
                BotTransaction.bot_type == "pubg",
                BotTransaction.status == "pending"  # Seulement pending, plus de processing
            ).order_by(BotTransaction.created_at.asc()).all()
            
            logger.info(f"Found {len(transactions)} pending transactions for all bots (1-10)")
            return transactions
            
        except Exception as e:
            logger.error(f"Error fetching pending transactions: {e}")
            return []
        finally:
            session.close()
    
    def mark_success(self, transaction_id: str, result: dict = None) -> bool:
        """
        Marquer une transaction comme réussie
        
        Args:
            transaction_id: ID de la transaction
            result: Résultat de l'automatisation (optionnel)
            
        Returns:
            True si la mise à jour a réussi
        """
        session = self.SessionLocal()
        try:
            transaction = session.query(BotTransaction).filter(
                BotTransaction.id == transaction_id
            ).first()
            
            if transaction:
                transaction.status = "success"
                
                # Mettre à jour le payload avec le résultat si fourni
                if result:
                    current_payload = transaction.payload or {}
                    current_payload['result'] = result
                    transaction.payload = current_payload
                
                session.commit()
                logger.info(f"Transaction {transaction_id} marked as success")
                return True
            else:
                logger.warning(f"Transaction {transaction_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error marking transaction {transaction_id} as success: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def mark_failed(self, transaction_id: str, error_message: str = None, increment_retry: bool = True, failure_reason: str = None) -> bool:
        """
        Marquer une transaction comme échouée
        
        Args:
            transaction_id: ID de la transaction
            error_message: Message d'erreur
            increment_retry: Incrémenter le compteur de retry
            failure_reason: Raison de l'échec (wrong_player_id, wrong_code, wrong_item_type, wrong_amount, wrong_email_password, other)
            
        Returns:
            True si la mise à jour a réussi
        """
        session = self.SessionLocal()
        try:
            transaction = session.query(BotTransaction).filter(
                BotTransaction.id == transaction_id
            ).first()
            
            if transaction:
                # Marquer directement comme failed (pas de retry dans la nouvelle architecture)
                transaction.status = "failure"
                
                # Ajouter la raison de l'échec
                if failure_reason:
                    transaction.failure_reason = failure_reason
                
                # Ajouter le message d'erreur dans le payload
                if error_message:
                    current_payload = transaction.payload or {}
                    current_payload['error_message'] = error_message
                    transaction.payload = current_payload
                session.commit()
                
                logger.info(f"Transaction {transaction_id} marked as failed with reason: {failure_reason}")
                return True
            else:
                logger.warning(f"Transaction {transaction_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error marking transaction {transaction_id} as failed: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_bot_stats(self, bot_num: int) -> dict:
        """
        Obtenir les statistiques d'un bot
        Ne compte plus les transactions "processing"
        
        Args:
            bot_num: Numéro du bot (1-10)
            
        Returns:
            Dictionnaire avec les statistiques
        """
        session = self.SessionLocal()
        try:
            # Compter les transactions par statut (sans processing)
            pending = session.query(BotTransaction).filter(
                BotTransaction.bot_num == bot_num,
                BotTransaction.status == "pending"
            ).count()
            
            # Plus de statut "processing" - supprimé
            processing = 0  # Toujours 0 maintenant
            
            success = session.query(BotTransaction).filter(
                BotTransaction.bot_num == bot_num,
                BotTransaction.status == "success"
            ).count()
            
            failed = session.query(BotTransaction).filter(
                BotTransaction.bot_num == bot_num,
                BotTransaction.status == "failed"
            ).count()
            
            total = pending + success + failed  # Plus de processing
            success_rate = (success / total * 100) if total > 0 else 0
            
            return {
                "bot_num": bot_num,
                "total_transactions": total,
                "pending": pending,
                "processing": processing,  # Toujours 0
                "success": success,
                "failed": failed,
                "success_rate": round(success_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for bot {bot_num}: {e}")
            return {}
        finally:
            session.close()
    
    def start_polling(self, callback):
        """
        Démarrer le polling (pour usage futur si nécessaire)
        
        Args:
            callback: Fonction à appeler quand des transactions sont trouvées
        """
        self.running = True
        logger.info("BotPoller started")
        
        while self.running:
            try:
                transactions = self.get_pending_transactions()
                if transactions and callback:
                    callback(transactions)
                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(self.poll_interval)
    
    def stop_polling(self):
        """Arrêter le polling"""
        self.running = False
        logger.info("BotPoller stopped")
