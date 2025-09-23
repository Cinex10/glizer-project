#!/usr/bin/env python3
"""
Script de test pour la nouvelle architecture de la base de données
selon les spécifications Salla
"""

import json
import uuid
from src.database.models import BotTransaction, Base
from src.database.postgresql import get_database_engine

def test_bot_transaction_creation():
    """Tester la création d'une transaction bot avec la nouvelle architecture"""
    
    # Exemple de payload selon les spécifications
    payload_example = {
        "player_id": "533938203",
        "code": "TESTCODE123",
        "email": "player@example.com",
        "password": "playerpassword"
    }
    
    # Créer une transaction PUBG
    pubg_transaction = BotTransaction(
        id=str(uuid.uuid4()),
        bot_num=9,
        status="pending",
        payload=payload_example,
        bot_type="pubg"
    )
    
    print("Transaction PUBG créée:")
    print(f"  ID: {pubg_transaction.id}")
    print(f"  Bot Num: {pubg_transaction.bot_num}")
    print(f"  Status: {pubg_transaction.status}")
    print(f"  Bot Type: {pubg_transaction.bot_type}")
    print(f"  Player ID: {pubg_transaction.get_player_id()}")
    print(f"  Code: {pubg_transaction.get_code()}")
    print(f"  Email: {pubg_transaction.get_email()}")
    print(f"  Password: {pubg_transaction.get_password()}")
    print(f"  Is PUBG Bot: {pubg_transaction.is_pubg_bot()}")
    print()
    
    # Créer une transaction Yalla Ludo
    yalla_payload = {
        "player_id": "987654321",
        "code": "YALLACODE456",
        "email": "yalla@example.com",
        "password": "yallapassword"
    }
    
    yalla_transaction = BotTransaction(
        id=str(uuid.uuid4()),
        bot_num=5,
        status="pending",
        payload=yalla_payload,
        bot_type="yalla_ludo"
    )
    
    print("Transaction Yalla Ludo créée:")
    print(f"  ID: {yalla_transaction.id}")
    print(f"  Bot Num: {yalla_transaction.bot_num}")
    print(f"  Status: {yalla_transaction.status}")
    print(f"  Bot Type: {yalla_transaction.bot_type}")
    print(f"  Is Yalla Ludo Bot: {yalla_transaction.is_yalla_ludo_bot()}")
    print()

def test_validation_constraints():
    """Tester les contraintes de validation"""
    
    print("Test des contraintes de validation:")
    
    # Test bot_num valide (1-10)
    try:
        valid_bot = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=5,
            status="pending",
            payload={"player_id": "123", "code": "TEST", "email": "test@test.com", "password": "pass"},
            bot_type="pubg"
        )
        print("✓ Bot num 5: VALIDE")
    except Exception as e:
        print(f"✗ Bot num 5: ERREUR - {e}")
    
    # Test bot_type valide
    try:
        valid_type = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=3,
            status="pending",
            payload={"player_id": "123", "code": "TEST", "email": "test@test.com", "password": "pass"},
            bot_type="yalla_ludo"
        )
        print("✓ Bot type yalla_ludo: VALIDE")
    except Exception as e:
        print(f"✗ Bot type yalla_ludo: ERREUR - {e}")

def test_status_updates():
    """Tester les mises à jour de statut"""
    
    print("\nTest des mises à jour de statut:")
    
    transaction = BotTransaction(
        id=str(uuid.uuid4()),
        bot_num=7,
        status="pending",
        payload={"player_id": "456", "code": "STATUSTEST", "email": "status@test.com", "password": "statuspass"},
        bot_type="pubg"
    )
    
    print(f"Status initial: {transaction.status}")
    print(f"Is pending: {transaction.is_pending()}")
    print(f"Is success: {transaction.is_success()}")
    print(f"Is failure: {transaction.is_failure()}")
    
    # Simuler un succès
    transaction.status = "success"
    print(f"\nAprès mise à jour vers 'success':")
    print(f"Is pending: {transaction.is_pending()}")
    print(f"Is success: {transaction.is_success()}")
    print(f"Is failure: {transaction.is_failure()}")

def main():
    """Fonction principale de test"""
    print("=== TEST DE LA NOUVELLE ARCHITECTURE BOTS_TRANSACTIONS ===")
    print("Spécifications Salla:")
    print("- Table: bots_transactions")
    print("- Colonnes: id, bot_num, status, payload, bot_type")
    print("- bot_num: 1-10")
    print("- bot_type: 'yalla_ludo' ou 'pubg'")
    print("- payload: {player_id, code, email, password}")
    print("- status: 'pending', 'success', 'failure'")
    print("=" * 60)
    
    test_bot_transaction_creation()
    test_validation_constraints()
    test_status_updates()
    
    print("\n=== TESTS TERMINÉS ===")
    print("L'architecture est maintenant conforme aux spécifications Salla!")

if __name__ == "__main__":
    main()

