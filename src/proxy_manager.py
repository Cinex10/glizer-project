"""
Gestionnaire de proxies simple et fiable pour les bots PUBG
Chaque bot (1-10) utilise automatiquement un proxy Webshare différent choisi aléatoirement
"""
import random
import threading
from typing import Dict, List, Tuple
from logging_config import get_logger

logger = get_logger(__name__)

class ProxyManager:
    def __init__(self):
        """Initialiser le gestionnaire de proxies avec la liste des proxies Webshare"""
        
        # Liste des proxies Webshare fournis
        self.proxies = [
            {"host": "142.111.48.253", "port": "7030", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "198.23.239.134", "port": "6540", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "45.38.107.97", "port": "6014", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "107.172.163.27", "port": "6543", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "64.137.96.74", "port": "6641", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "154.203.43.247", "port": "5536", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "84.247.60.125", "port": "6095", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "216.10.27.159", "port": "6837", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "142.111.67.146", "port": "5611", "username": "liyhrdvw", "password": "r985mvazz8en"},
            {"host": "142.147.128.93", "port": "6593", "username": "liyhrdvw", "password": "r985mvazz8en"}
        ]
        
        # Dictionnaire pour tracker les proxies utilisés par chaque bot
        self.bot_proxies: Dict[int, Dict] = {}
        self.lock = threading.Lock()
        
        logger.info(f"ProxyManager initialisé avec {len(self.proxies)} proxies disponibles")
    
    def get_proxy_for_bot(self, bot_num: int) -> Dict:
        """
        Obtenir un proxy aléatoire pour un bot spécifique
        Chaque bot aura un proxy différent et fixe pendant sa session
        
        Args:
            bot_num: Numéro du bot (1-10)
            
        Returns:
            Dictionnaire contenant les informations du proxy
        """
        with self.lock:
            # Si le bot a déjà un proxy assigné, le retourner
            if bot_num in self.bot_proxies:
                proxy = self.bot_proxies[bot_num]
                logger.info(f"Bot {bot_num}: Réutilisation du proxy {proxy['host']}:{proxy['port']}")
                return proxy
            
            # Obtenir les proxies déjà utilisés par d'autres bots
            used_proxies = set()
            for used_proxy in self.bot_proxies.values():
                used_proxies.add((used_proxy['host'], used_proxy['port']))
            
            # Trouver les proxies disponibles
            available_proxies = []
            for proxy in self.proxies:
                if (proxy['host'], proxy['port']) not in used_proxies:
                    available_proxies.append(proxy)
            
            # Si tous les proxies sont utilisés, choisir aléatoirement parmi tous
            if not available_proxies:
                logger.warning(f"Tous les proxies sont utilisés, attribution aléatoire pour bot {bot_num}")
                available_proxies = self.proxies
            
            # Choisir un proxy aléatoire parmi les disponibles
            selected_proxy = random.choice(available_proxies)
            
            # Assigner le proxy au bot
            self.bot_proxies[bot_num] = selected_proxy
            
            logger.info(f"Bot {bot_num}: Nouveau proxy assigné {selected_proxy['host']}:{selected_proxy['port']}")
            return selected_proxy
    
    def release_bot_proxy(self, bot_num: int):
        """
        Libérer le proxy d'un bot (quand le bot s'arrête)
        
        Args:
            bot_num: Numéro du bot (1-10)
        """
        with self.lock:
            if bot_num in self.bot_proxies:
                proxy = self.bot_proxies[bot_num]
                del self.bot_proxies[bot_num]
                logger.info(f"Bot {bot_num}: Proxy {proxy['host']}:{proxy['port']} libéré")
    
    def get_seleniumwire_options(self, bot_num: int) -> Dict:
        """
        Obtenir les options Selenium Wire pour un bot spécifique
        
        Args:
            bot_num: Numéro du bot (1-10)
            
        Returns:
            Dictionnaire des options Selenium Wire
        """
        proxy = self.get_proxy_for_bot(bot_num)
        
        seleniumwire_options = {
            'proxy': {
                'http': f'http://{proxy["username"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}',
                'https': f'https://{proxy["username"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}',
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
        
        logger.info(f"Bot {bot_num}: Options Selenium Wire configurées pour proxy {proxy['host']}:{proxy['port']}")
        return seleniumwire_options
    
    def get_proxy_status(self) -> Dict:
        """
        Obtenir le statut actuel des proxies
        
        Returns:
            Dictionnaire avec les informations sur l'utilisation des proxies
        """
        with self.lock:
            return {
                "total_proxies": len(self.proxies),
                "used_proxies": len(self.bot_proxies),
                "available_proxies": len(self.proxies) - len(self.bot_proxies),
                "bot_assignments": dict(self.bot_proxies)
            }

# Instance globale du gestionnaire de proxies
proxy_manager = ProxyManager()

