#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion PostgreSQL et créer des données de test
"""
import json
import uuid
from datetime import datetime
from database.postgresql import get_postgres_session, close_postgres_connection
from database.models import BotTransaction
from logging_config import get_logger

logger = get_logger(__name__)

def test_connection():
    """Tester la connexion PostgreSQL"""
    logger.info("Testing PostgreSQL connection...")
    
    session = get_postgres_session()
    try:
        # Test simple
        result = session.execute("SELECT 1 as test")
        test_value = result.fetchone()[0]
        
        if test_value == 1:
            logger.info("✅ PostgreSQL connection successful")
            return True
        else:
            logger.error("❌ PostgreSQL connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False
    finally:
        session.close()

def create_test_transactions():
    """Créer des transactions de test pour les bots 9 et 10"""
    logger.info("Creating test transactions...")
    
    session = get_postgres_session()
    try:
        # Transactions de test pour bot 9
        test_transactions_bot9 = [
            {
                "id": str(uuid.uuid4()),
                "bot_num": 9,
                "status": "pending",
                "payload": {
                    "player_id": "533938203",
                    "code": "TEST_CODE_9_1"
                },
                "bot_type": "pubg"
            },
            {
                "id": str(uuid.uuid4()),
                "bot_num": 9,
                "status": "pending", 
                "payload": {
                    "player_id": "533938204",
                    "code": "TEST_CODE_9_3"
                },
                "bot_type": "pubg"
            }
        ]
        
        # Transactions de test pour bot 10
        test_transactions_bot10 = [
            {
                "id": str(uuid.uuid4()),
                "bot_num": 10,
                "status": "pending",
                "payload": {
                    "player_id": "533938205", 
                    "code": "TEST_CODE_10_1"
                },
                "bot_type": "pubg"
            },
            {
                "id": str(uuid.uuid4()),
                "bot_num": 10,
                "status": "pending",
                "payload": {
                    "player_id": "533938206",
                    "code": "TEST_CODE_10_2"
                },
                "bot_type": "pubg"
            }
        ]
        
        all_transactions = test_transactions_bot9 + test_transactions_bot10
        
        for tx_data in all_transactions:
            transaction = BotTransaction(**tx_data)
            session.add(transaction)
        
        session.commit()
        logger.info(f"✅ Created {len(all_transactions)} test transactions")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create test transactions: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def list_pending_transactions():
    """Lister les transactions en attente"""
    logger.info("Listing pending transactions...")
    
    session = get_postgres_session()
    try:
        pending = session.query(BotTransaction).filter(
            BotTransaction.bot_num.in_([9, 10]),
            BotTransaction.bot_type == "pubg",
            BotTransaction.status == "pending"
        ).all()
        
        logger.info(f"Found {len(pending)} pending transactions:")
        for tx in pending:
            logger.info(f"  - {tx.id}: Bot {tx.bot_num}, Player {tx.get_player_id()}, Codes: {len(tx.get_redeem_codes())}")
        
        return len(pending)
        
    except Exception as e:
        logger.error(f"❌ Failed to list transactions: {e}")
        return 0
    finally:
        session.close()

def cleanup_test_data():
    """Nettoyer les données de test"""
    logger.info("Cleaning up test data...")
    
    session = get_postgres_session()
    try:
        # Supprimer les transactions de test
        deleted = session.query(BotTransaction).filter(
            BotTransaction.payload.op('->>')('player_id').like('53393820%')
        ).delete()
        
        session.commit()
        logger.info(f"✅ Cleaned up {deleted} test transactions")
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup: {e}")
        session.rollback()
    finally:
        session.close()

def main():
    """Fonction principale de test"""
    logger.info("🧪 Starting PostgreSQL test suite...")
    
    try:
        # Test 1: Connexion
        if not test_connection():
            logger.error("Connection test failed, exiting")
            return
        
        # Test 2: Créer des données de test
        if not create_test_transactions():
            logger.error("Failed to create test data")
            return
        
        # Test 3: Lister les transactions
        count = list_pending_transactions()
        if count == 0:
            logger.warning("No pending transactions found")
        
        # Test 4: Nettoyer (optionnel)
        cleanup_choice = input("Clean up test data? (y/N): ").lower().strip()
        if cleanup_choice in ['y', 'yes']:
            cleanup_test_data()
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
    finally:
        close_postgres_connection()

if __name__ == "__main__":
    main()

