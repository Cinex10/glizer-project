"""
Gestionnaire de rotation aléatoire des credentials
"""
import json
import os
import random
import threading
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from logging_config import get_logger

logger = get_logger(__name__)

class CredentialManager:
    def __init__(self, config_file: str = "config/accounts.json"):
        """
        Initialiser le gestionnaire de credentials avec rotation séquentielle
        
        Args:
            config_file: Chemin vers le fichier de configuration des credentials
        """
        # Créer le dossier config s'il n'existe pas
        config_dir = os.path.dirname(config_file)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"Config directory ensured: {config_dir}")
        
        self.config_file = config_file
        self.credentials: List[Dict] = []
        self.lock = threading.Lock()
        self.usage_stats = {}  # Statistiques d'utilisation par credential
        
        # Système de tracking des emails en cours d'utilisation
        self.active_emails: Set[str] = set()  # Emails actuellement utilisés par des bots
        self.email_usage_lock = threading.Lock()  # Lock pour la thread safety
        
        # Système de rotation séquentielle
        self.current_position = 0  # Position actuelle dans la rotation
        self.rotation_mode = "sequential"  # Mode de rotation
        
        # Charger les credentials
        self._load_credentials()
        
        logger.info(f"CredentialManager initialized with {len(self.credentials)} credentials using SEQUENTIAL rotation")
    
    def _load_credentials(self):
        """Charger les credentials depuis le fichier de configuration"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Credentials file not found: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Nouveau format avec accounts array
            if isinstance(data, dict) and 'accounts' in data:
                self.credentials = data['accounts']
            else:
                # Ancien format (compatibilité)
                self.credentials = data if isinstance(data, list) else []
            
            if not self.credentials:
                raise ValueError("No credentials found in configuration file")
            
            # Initialiser les statistiques d'utilisation
            for cred in self.credentials:
                cred_id = cred.get('id', len(self.usage_stats))
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
    
    def _save_stats(self):
        """Sauvegarder les statistiques d'utilisation dans le fichier principal"""
        try:
            # Créer le dossier parent s'il n'existe pas
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            # Charger le fichier existant
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Ajouter les statistiques
            data['usage_stats'] = self.usage_stats
            data['last_updated'] = datetime.utcnow().isoformat()
            
            # Sauvegarder
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save usage stats: {e}")
    
    def get_next_credential(self, exclude_emails: set = None) -> Tuple[Dict, int]:
        """
        Obtenir le prochain credential dans la rotation séquentielle en évitant les emails déjà utilisés
        
        Args:
            exclude_emails: Set d'emails à éviter (emails déjà utilisés par d'autres bots)
        
        Returns:
            Tuple (credential_dict, credential_index)
        """
        with self.lock:
            if not self.credentials:
                raise Exception("No credentials available")
            
            # Combiner les emails exclus avec les emails actuellement utilisés
            with self.email_usage_lock:
                all_excluded_emails = set(self.active_emails)
                if exclude_emails:
                    all_excluded_emails.update(exclude_emails)
            
            # Trouver le prochain credential disponible dans la séquence
            selected_cred = None
            original_index = None
            attempts = 0
            max_attempts = len(self.credentials)
            
            while attempts < max_attempts:
                # Utiliser la position actuelle dans la rotation
                current_cred = self.credentials[self.current_position]
                
                # Vérifier si ce credential est disponible
                if current_cred['email'] not in all_excluded_emails:
                    selected_cred = current_cred.copy()
                    original_index = self.current_position
                    break
                
                # Passer au suivant dans la séquence
                self.current_position = (self.current_position + 1) % len(self.credentials)
                attempts += 1
            
            # Si aucun credential n'est disponible, utiliser le premier
            if selected_cred is None:
                logger.warning("All emails are excluded or in use, using first available credential")
                selected_cred = self.credentials[0].copy()
                original_index = 0
                self.current_position = 1  # Position suivante pour la prochaine fois
            
            # Avancer la position pour la prochaine utilisation
            if selected_cred is not None and original_index is not None:
                self.current_position = (original_index + 1) % len(self.credentials)
            
            # Marquer l'email comme actif
            with self.email_usage_lock:
                self.active_emails.add(selected_cred['email'])
                logger.info(f"🔒 Email {selected_cred['email']} marked as active (total active: {len(self.active_emails)})")
            
            # Mettre à jour les statistiques
            cred_id = selected_cred.get('id', original_index)
            self.usage_stats[str(cred_id)]['usage_count'] += 1
            self.usage_stats[str(cred_id)]['last_used'] = datetime.utcnow().isoformat()
            
            # Sauvegarder les statistiques
            self._save_stats()
            
            logger.info(f"🔄 SEQUENTIAL selection: Using credential {cred_id} ({selected_cred['email']}) - index {original_index} (next position: {self.current_position})")
            
            return selected_cred, original_index
    
    def mark_credential_success(self, credential_index: int):
        """Marquer un credential comme ayant réussi"""
        try:
            if 0 <= credential_index < len(self.credentials):
                cred_id = self.credentials[credential_index].get('id', credential_index)
                self.usage_stats[str(cred_id)]['success_count'] += 1
                self._save_stats()
                logger.debug(f"✅ Credential {cred_id} marked as success")
        except Exception as e:
            logger.error(f"Failed to mark credential success: {e}")
    
    def mark_credential_failed(self, credential_index: int):
        """Marquer un credential comme ayant échoué"""
        try:
            if 0 <= credential_index < len(self.credentials):
                cred_id = self.credentials[credential_index].get('id', credential_index)
                self.usage_stats[str(cred_id)]['failed_count'] += 1
                self._save_stats()
                logger.debug(f"❌ Credential {cred_id} marked as failed")
        except Exception as e:
            logger.error(f"Failed to mark credential failed: {e}")
    
    def get_credential_by_index(self, index: int) -> Optional[Dict]:
        """Obtenir un credential par son index"""
        if 0 <= index < len(self.credentials):
            return self.credentials[index].copy()
        return None
    
    def get_usage_stats(self) -> Dict:
        """Obtenir les statistiques d'utilisation avec rotation séquentielle"""
        with self.email_usage_lock:
            active_emails = list(self.active_emails)
            available_emails = [cred['email'] for cred in self.credentials if cred['email'] not in self.active_emails]
        
        # Calculer le progrès de rotation
        rotation_progress = (self.current_position / len(self.credentials)) * 100 if self.credentials else 0
        
        return {
            'rotation_mode': self.rotation_mode,
            'current_position': self.current_position,
            'total_credentials': len(self.credentials),
            'rotation_progress': round(rotation_progress, 2),
            'usage_stats': self.usage_stats.copy(),
            'available_credentials': len(self.credentials),
            'active_emails': active_emails,
            'active_emails_count': len(active_emails),
            'available_emails': available_emails,
            'available_emails_count': len(available_emails)
        }
    
    def get_credential_stats(self, credential_id: int) -> Optional[Dict]:
        """Obtenir les statistiques d'un credential spécifique"""
        return self.usage_stats.get(str(credential_id))
    
    def get_random_credential(self) -> Tuple[Dict, int]:
        """Obtenir un credential aléatoire (alias pour get_next_credential)"""
        return self.get_next_credential()
    
    def get_available_credentials_count(self) -> int:
        """Obtenir le nombre de credentials disponibles"""
        return len(self.credentials)
    
    def reset_rotation(self, index: int = 0):
        """
        Réinitialiser la rotation des credentials à une position donnée
        
        Args:
            index: Position à laquelle remettre la rotation (défaut: 0)
        """
        with self.lock:
            if 0 <= index < len(self.credentials):
                self.current_position = index
                logger.info(f"🔄 Rotation reset to position {index}")
            else:
                logger.warning(f"Invalid rotation index {index}, resetting to 0")
                self.current_position = 0
    
    def get_current_position(self) -> int:
        """
        Obtenir la position actuelle dans la rotation
        
        Returns:
            Position actuelle (0-based)
        """
        return self.current_position
    
    def force_next_credential(self) -> Tuple[Dict, int]:
        """
        Forcer l'utilisation du prochain credential dans la séquence (sans l'utiliser)
        
        Returns:
            Tuple (credential_dict, credential_index) du prochain credential
        """
        with self.lock:
            if not self.credentials:
                raise Exception("No credentials available")
            
            # Obtenir le credential à la position actuelle
            next_cred = self.credentials[self.current_position].copy()
            next_index = self.current_position
            
            logger.info(f"🔄 Force next credential: {next_cred['email']} at position {next_index}")
            
            return next_cred, next_index
    
    def is_credential_available(self, index: int) -> bool:
        """Vérifier si un credential est disponible"""
        return 0 <= index < len(self.credentials)
    
    def release_email(self, email: str):
        """
        Libérer un email marqué comme actif
        
        Args:
            email: Email à libérer
        """
        with self.email_usage_lock:
            if email in self.active_emails:
                self.active_emails.remove(email)
                logger.info(f"🔓 Email {email} released (remaining active: {len(self.active_emails)})")
            else:
                logger.warning(f"Email {email} was not marked as active")
    
    def is_email_available(self, email: str) -> bool:
        """
        Vérifier si un email est disponible (pas utilisé par un autre bot)
        
        Args:
            email: Email à vérifier
            
        Returns:
            True si l'email est disponible, False sinon
        """
        with self.email_usage_lock:
            return email not in self.active_emails
    
    def get_available_emails(self) -> List[str]:
        """
        Obtenir la liste des emails disponibles (non utilisés)
        
        Returns:
            Liste des emails disponibles
        """
        with self.email_usage_lock:
            return [cred['email'] for cred in self.credentials if cred['email'] not in self.active_emails]
    
    def get_active_emails(self) -> Set[str]:
        """
        Obtenir la liste des emails actuellement utilisés
        
        Returns:
            Set des emails actifs
        """
        with self.email_usage_lock:
            return self.active_emails.copy()
    
    def force_release_all_emails(self):
        """
        Forcer la libération de tous les emails (pour maintenance)
        """
        with self.email_usage_lock:
            released_count = len(self.active_emails)
            released_emails = list(self.active_emails)
            self.active_emails.clear()
            logger.warning(f"🔓 Force released {released_count} emails: {released_emails}")
            return {
                "released_count": released_count,
                "released_emails": released_emails
            }
    
    def test_email_availability(self, exclude_emails: set = None) -> Dict:
        """
        Tester la disponibilité des emails et retourner un email unique
        
        Args:
            exclude_emails: Set d'emails à éviter (emails déjà utilisés par d'autres bots)
            
        Returns:
            Dict avec les informations de test
        """
        if not exclude_emails:
            exclude_emails = set()
        
        # Combiner avec les emails actuellement utilisés
        with self.email_usage_lock:
            all_excluded_emails = set(self.active_emails)
            all_excluded_emails.update(exclude_emails)
        
        # Compter les emails disponibles
        available_emails = []
        excluded_emails = []
        
        for cred in self.credentials:
            if cred['email'] in all_excluded_emails:
                excluded_emails.append(cred['email'])
            else:
                available_emails.append(cred['email'])
        
        # Sélectionner un email aléatoire parmi les disponibles
        if available_emails:
            selected_email = random.choice(available_emails)
            selected_cred = next(cred for cred in self.credentials if cred['email'] == selected_email)
        else:
            # Si aucun email disponible, utiliser le premier
            selected_cred = self.credentials[0]
            selected_email = selected_cred['email']
            logger.warning("No available emails, using first credential")
        
        return {
            "selected_email": selected_email,
            "selected_credential_id": selected_cred.get('id'),
            "available_emails_count": len(available_emails),
            "excluded_emails_count": len(excluded_emails),
            "excluded_emails": list(excluded_emails),
            "active_emails": list(self.active_emails),
            "total_credentials": len(self.credentials),
            "is_unique": selected_email not in all_excluded_emails
        }