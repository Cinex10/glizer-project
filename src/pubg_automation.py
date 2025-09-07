"""
Wrapper pour le service PUBG existant - adapté pour la nouvelle architecture
"""
import os
import json
import time
import random
from pubg.service import process_pubg_recharge
from logging_config import get_logger

logger = get_logger(__name__)

class PubgAutomation:
    def __init__(self, email: str):
        self.email = email
        # Le user data sera géré automatiquement par le service existant
        # qui utilise déjà user-data-{email} comme dossier
        
    def process_redeem_codes(self, password: str, player_id: str, redeem_codes: list):
        """Traiter les codes de rédemption en utilisant le service existant"""
        
        try:
            logger.info(f"Starting PUBG automation for email: {self.email}")
            logger.info(f"Player ID: {player_id}")
            logger.info(f"Number of codes: {len(redeem_codes)}")
            
            # Utiliser le service existant qui fonctionne bien
            result = process_pubg_recharge(
                emailAddress=self.email,
                password=password,
                playerId=player_id,
                redeemCodes=redeem_codes
            )
            
            logger.info(f"PUBG automation completed for {self.email}")
            return result
            
        except Exception as e:
            logger.error(f"PUBG automation failed for {self.email}: {e}")
            raise e

def process_pubg_transaction(email: str, password: str, player_id: str, redeem_codes: list):
    """Fonction principale pour traiter une transaction PUBG"""
    
    automation = PubgAutomation(email)
    return automation.process_redeem_codes(password, player_id, redeem_codes)
