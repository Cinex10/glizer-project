#!/usr/bin/env python3
"""
Exemple d'intégration avec les données Salla
Montre comment traiter les vraies requêtes venant de Salla
"""

import json
import uuid
from sqlalchemy.orm import sessionmaker
from src.database.models import BotTransaction, Base
from src.database.postgresql import get_database_engine

class SallaTransactionProcessor:
    """Processeur pour les transactions Salla"""
    
    def __init__(self):
        self.engine = get_database_engine()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def create_transaction_from_salla(self, salla_data):
        """
        Créer une transaction à partir des données Salla
        
        Args:
            salla_data (dict): Données venant de Salla avec:
                - bot_num: entier de 1 à 10
                - bot_type: "yalla_ludo" ou "pubg"
                - payload: {player_id, code, email, password}
        """
        try:
            # Validation des données
            if not self._validate_salla_data(salla_data):
                return None, "Données Salla invalides"
            
            # Créer la transaction
            transaction = BotTransaction(
                id=str(uuid.uuid4()),
                bot_num=salla_data['bot_num'],
                status="pending",
                payload=salla_data['payload'],
                bot_type=salla_data['bot_type']
            )
            
            # Sauvegarder en base
            self.session.add(transaction)
            self.session.commit()
            
            return transaction, "Transaction créée avec succès"
            
        except Exception as e:
            self.session.rollback()
            return None, f"Erreur lors de la création: {str(e)}"
    
    def _validate_salla_data(self, data):
        """Valider les données venant de Salla"""
        required_fields = ['bot_num', 'bot_type', 'payload']
        
        # Vérifier les champs requis
        for field in required_fields:
            if field not in data:
                print(f"Champ manquant: {field}")
                return False
        
        # Vérifier bot_num (1-10)
        if not isinstance(data['bot_num'], int) or not (1 <= data['bot_num'] <= 10):
            print(f"bot_num invalide: {data['bot_num']}")
            return False
        
        # Vérifier bot_type
        if data['bot_type'] not in ['yalla_ludo', 'pubg']:
            print(f"bot_type invalide: {data['bot_type']}")
            return False
        
        # Vérifier payload
        payload = data['payload']
        payload_fields = ['player_id', 'code', 'email', 'password']
        
        for field in payload_fields:
            if field not in payload:
                print(f"Champ payload manquant: {field}")
                return False
        
        return True
    
    def update_transaction_status(self, transaction_id, new_status):
        """
        Mettre à jour le statut d'une transaction
        
        Args:
            transaction_id (str): ID de la transaction
            new_status (str): Nouveau statut ('success' ou 'failure')
        """
        try:
            transaction = self.session.query(BotTransaction).filter_by(id=transaction_id).first()
            
            if not transaction:
                return False, "Transaction non trouvée"
            
            if new_status not in ['success', 'failure']:
                return False, "Statut invalide"
            
            transaction.status = new_status
            self.session.commit()
            
            return True, f"Statut mis à jour vers: {new_status}"
            
        except Exception as e:
            self.session.rollback()
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def get_pending_transactions(self, bot_num=None, bot_type=None):
        """Récupérer les transactions en attente"""
        query = self.session.query(BotTransaction).filter_by(status="pending")
        
        if bot_num:
            query = query.filter_by(bot_num=bot_num)
        
        if bot_type:
            query = query.filter_by(bot_type=bot_type)
        
        return query.all()
    
    def process_transaction(self, transaction):
        """
        Traiter une transaction (exécuter l'opération)
        Cette méthode doit être adaptée selon votre logique métier
        """
        try:
            print(f"Traitement de la transaction {transaction.id}")
            print(f"  Bot: {transaction.bot_num} ({transaction.bot_type})")
            print(f"  Player ID: {transaction.get_player_id()}")
            print(f"  Code: {transaction.get_code()}")
            print(f"  Email: {transaction.get_email()}")
            
            # Ici vous implémenterez votre logique d'automatisation
            # Pour PUBG ou Yalla Ludo selon le bot_type
            
            if transaction.is_pubg_bot():
                success = self._process_pubg_transaction(transaction)
            elif transaction.is_yalla_ludo_bot():
                success = self._process_yalla_ludo_transaction(transaction)
            else:
                success = False
            
            # Mettre à jour le statut
            new_status = "success" if success else "failure"
            self.update_transaction_status(transaction.id, new_status)
            
            return success
            
        except Exception as e:
            print(f"Erreur lors du traitement: {str(e)}")
            self.update_transaction_status(transaction.id, "failure")
            return False
    
    def _process_pubg_transaction(self, transaction):
        """Traiter une transaction PUBG"""
        # Votre logique d'automatisation PUBG ici
        print("  → Traitement PUBG...")
        # Simuler le traitement
        return True  # ou False selon le résultat
    
    def _process_yalla_ludo_transaction(self, transaction):
        """Traiter une transaction Yalla Ludo"""
        # Votre logique d'automatisation Yalla Ludo ici
        print("  → Traitement Yalla Ludo...")
        # Simuler le traitement
        return True  # ou False selon le résultat

def example_usage():
    """Exemple d'utilisation avec des données Salla"""
    
    processor = SallaTransactionProcessor()
    
    # Exemple de données venant de Salla
    salla_requests = [
        {
            "bot_num": 9,
            "bot_type": "pubg",
            "payload": {
                "player_id": "533938203",
                "code": "PUBGCODE123",
                "email": "player@example.com",
                "password": "playerpassword"
            }
        },
        {
            "bot_num": 5,
            "bot_type": "yalla_ludo",
            "payload": {
                "player_id": "987654321",
                "code": "YALLACODE456",
                "email": "yalla@example.com",
                "password": "yallapassword"
            }
        }
    ]
    
    print("=== TRAITEMENT DES REQUÊTES SALLA ===")
    
    # Traiter chaque requête
    for i, request in enumerate(salla_requests, 1):
        print(f"\n--- Requête {i} ---")
        
        # Créer la transaction
        transaction, message = processor.create_transaction_from_salla(request)
        
        if transaction:
            print(f"✓ {message}")
            print(f"  ID: {transaction.id}")
            
            # Traiter la transaction
            success = processor.process_transaction(transaction)
            print(f"  Résultat: {'✓ SUCCÈS' if success else '✗ ÉCHEC'}")
        else:
            print(f"✗ {message}")
    
    # Afficher les transactions en attente
    print("\n--- Transactions en attente ---")
    pending = processor.get_pending_transactions()
    for tx in pending:
        print(f"  {tx.id}: Bot {tx.bot_num} ({tx.bot_type}) - {tx.status}")

if __name__ == "__main__":
    example_usage()

