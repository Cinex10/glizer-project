"""
Wrapper pour le service PUBG existant - adapté pour la nouvelle architecture PostgreSQL
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
            
            # Validation des paramètres
            if not player_id or not isinstance(player_id, str):
                raise Exception(f"Invalid player_id: {player_id}")
            
            if not redeem_codes or not isinstance(redeem_codes, list):
                raise Exception(f"Invalid redeem_codes: {redeem_codes}")
            
            if not password:
                raise Exception("Password is required")
            
            # Utiliser le service existant qui fonctionne bien
            result = process_pubg_recharge(
                emailAddress=self.email,
                password=password,
                playerId=player_id,
                redeemCodes=redeem_codes
            )
            
            # Vérifier que le résultat est valide
            if not result:
                raise Exception("PUBG service returned empty result")
            
            if not isinstance(result, dict):
                raise Exception(f"PUBG service returned invalid result type: {type(result)}")
            
            # Vérifier qu'on a un résultat pour chaque code
            for code in redeem_codes:
                if code not in result:
                    logger.warning(f"Missing result for code: {code}")
                    result[code] = "Missing result from PUBG service"
            
            logger.info(f"PUBG automation completed for {self.email}: {result}")
            return result
            
        except Exception as e:
            error_msg = f"PUBG automation failed for {self.email}: {str(e)}"
            logger.error(error_msg)
            
            # Créer un résultat d'erreur pour tous les codes
            error_result = {}
            if redeem_codes and isinstance(redeem_codes, list):
                for code in redeem_codes:
                    error_result[code] = f"Automation failed: {str(e)}"
            
            # Re-lever l'exception pour que le transaction_processor puisse la capturer
            raise Exception(error_msg)

def process_pubg_transaction(email: str, password: str, player_id: str, redeem_codes: list):
    """
    Fonction principale pour traiter une transaction PUBG
    Adaptée pour fonctionner avec les bots 9 et 10
    """
    
    automation = PubgAutomation(email)
    return automation.process_redeem_codes(password, player_id, redeem_codes)