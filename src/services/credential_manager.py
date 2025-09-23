"""
Gestionnaire de rotation des credentials
"""
import json
import os
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from logging_config import get_logger

logger = get_logger(__name__)

class CredentialManager:
    def __init__(self, config_file: str = "config/confidential.json", state_file: str = "config/rotation_state.json"):
        """
        Initialiser le gestionnaire de credentials
        
        Args:
            config_file: Chemin vers le fichier de configuration des credentials
            state_file: Chemin vers le fichier de persistance de l'état
        """
        # Créer le dossier config s'il n'existe pas
        config_dir = os.path.dirname(config_file)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"Config directory ensured: {config_dir}")
        
        self.config_file = config_file
        self.state_file = state_file
        self.credentials: List[Dict] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.usage_stats = {}  # Statistiques d'utilisation par credential
        
        # Charger les credentials et l'état
        self._load_credentials()
        self._load_state()
        
        logger.info(f"CredentialManager initialized with {len(self.credentials)} credentials")
    
    def _load_credentials(self):
        """Charger les credentials depuis le fichier de configuration"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Credentials file not found: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                self.credentials = json.load(f)
            
            if not self.credentials:
                raise ValueError("No credentials found in configuration file")
            
            # Initialiser les statistiques d'utilisation
            for i, cred in enumerate(self.credentials):
                cred_id = cred.get('id', i)
                self.usage_stats[str(cred_id)] = {
                    'email': cred['email'],
                    'usage_count': 0,
                    'last_used': None,
                    'success_count': 0,
                    'failed_count': 0
                }
            
            logger.info(f"Loaded {len(self.credentials)} credentials from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise
    
    def _load_state(self):
        """Charger l'état de rotation depuis le fichier de persistance"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.current_index = state.get('current_index', 0)
                    
                    # Charger les statistiques si disponibles
                    saved_stats = state.get('usage_stats', {})
                    for cred_id, stats in saved_stats.items():
                        if str(cred_id) in self.usage_stats:
                            self.usage_stats[str(cred_id)].update(stats)
                
                logger.info(f"Loaded rotation state: current_index={self.current_index}")
            else:
                logger.info("No rotation state file found, starting from index 0")
                
        except Exception as e:
            logger.warning(f"Failed to load rotation state: {e}, starting from index 0")
            self.current_index = 0
    
    def _save_state(self):
        """Sauvegarder l'état de rotation"""
        try:
            # Créer le dossier parent s'il n'existe pas
            state_dir = os.path.dirname(self.state_file)
            if state_dir:
                os.makedirs(state_dir, exist_ok=True)
            
            state = {
                'current_index': self.current_index,
                'usage_stats': self.usage_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save rotation state: {e}")
    
    def get_next_credential(self) -> Tuple[Dict, int]:
        """
        Obtenir le prochain credential dans la rotation
        
        Returns:
            Tuple (credential_dict, credential_index)
        """
        with self.lock:
            if not self.credentials:
                raise Exception("No credentials available")
            
            # Obtenir le credential actuel
            current_cred = self.credentials[self.current_index].copy()
            current_index = self.current_index
            
            # Mettre à jour les statistiques
            cred_id = current_cred.get('id', current_index)
            self.usage_stats[str(cred_id)]['usage_count'] += 1
            self.usage_stats[str(cred_id)]['last_used'] = datetime.utcnow().isoformat()
            
            # Passer au suivant (avec reset automatique)
            self.current_index = (self.current_index + 1) % len(self.credentials)
            
            # Sauvegarder l'état
            self._save_state()
            
            logger.info(f"Using credential {cred_id} ({current_cred['email']}) - next will be index {self.current_index}")
            
            return current_cred, current_index
    
    def mark_credential_success(self, credential_index: int):
        """Marquer un credential comme ayant réussi"""
        try:
            if 0 <= credential_index < len(self.credentials):
                cred_id = self.credentials[credential_index].get('id', credential_index)
                self.usage_stats[str(cred_id)]['success_count'] += 1
                self._save_state()
                logger.debug(f"Credential {cred_id} marked as success")
        except Exception as e:
            logger.error(f"Failed to mark credential success: {e}")
    
    def mark_credential_failed(self, credential_index: int):
        """Marquer un credential comme ayant échoué"""
        try:
            if 0 <= credential_index < len(self.credentials):
                cred_id = self.credentials[credential_index].get('id', credential_index)
                self.usage_stats[str(cred_id)]['failed_count'] += 1
                self._save_state()
                logger.debug(f"Credential {cred_id} marked as failed")
        except Exception as e:
            logger.error(f"Failed to mark credential failed: {e}")
    
    def get_credential_by_index(self, index: int) -> Optional[Dict]:
        """Obtenir un credential par son index"""
        if 0 <= index < len(self.credentials):
            return self.credentials[index].copy()
        return None
    
    def get_current_position(self) -> int:
        """Obtenir la position actuelle dans la rotation"""
        return self.current_index
    
    def reset_rotation(self, index: int = 0):
        """Réinitialiser la rotation à un index spécifique"""
        with self.lock:
            if 0 <= index < len(self.credentials):
                self.current_index = index
                self._save_state()
                logger.info(f"Rotation reset to index {index}")
            else:
                logger.error(f"Invalid reset index: {index}")
    
    def get_usage_stats(self) -> Dict:
        """Obtenir les statistiques d'utilisation"""
        return {
            'current_position': self.current_index,
            'total_credentials': len(self.credentials),
            'usage_stats': self.usage_stats.copy(),
            'rotation_progress': f"{self.current_index}/{len(self.credentials)}"
        }
    
    def get_credential_stats(self, credential_id: int) -> Optional[Dict]:
        """Obtenir les statistiques d'un credential spécifique"""
        return self.usage_stats.get(str(credential_id))
    
    def force_next_credential(self) -> Tuple[Dict, int]:
        """Forcer l'utilisation du prochain credential (pour tests/maintenance)"""
        with self.lock:
            # Avancer manuellement l'index
            self.current_index = (self.current_index + 1) % len(self.credentials)
            self._save_state()
            
            return self.get_next_credential()
    
    def get_available_credentials_count(self) -> int:
        """Obtenir le nombre de credentials disponibles"""
        return len(self.credentials)
    
    def is_credential_available(self, index: int) -> bool:
        """Vérifier si un credential est disponible"""
        return 0 <= index < len(self.credentials)