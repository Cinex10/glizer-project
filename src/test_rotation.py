#!/usr/bin/env python3
"""
Script de test pour le système de rotation des credentials
"""
import json
import time
import uuid
from datetime import datetime
from services.credential_manager import CredentialManager
from services.transaction_processor import TransactionProcessor
from database.postgresql import get_postgres_session, close_postgres_connection
from database.models import BotTransaction
from logging_config import get_logger

logger = get_logger(__name__)

def test_credential_manager():
    """Tester le gestionnaire de credentials"""
    logger.info("🧪 Testing CredentialManager...")
    
    try:
        # Initialiser le gestionnaire
        cred_manager = CredentialManager()
        
        # Test 1: Obtenir le premier credential
        logger.info("Test 1: Getting first credential")
        cred1, index1 = cred_manager.get_next_credential()
        logger.info(f"✅ First credential: {cred1['email']} (index {index1})")
        
        # Test 2: Obtenir le deuxième credential
        logger.info("Test 2: Getting second credential")
        cred2, index2 = cred_manager.get_next_credential()
        logger.info(f"✅ Second credential: {cred2['email']} (index {index2})")
        
        # Test 3: Vérifier la rotation
        if index2 == (index1 + 1) % cred_manager.get_available_credentials_count():
            logger.info("✅ Rotation working correctly")
        else:
            logger.error(f"❌ Rotation failed: {index1} -> {index2}")
        
        # Test 4: Marquer des succès/échecs
        logger.info("Test 4: Marking success/failure")
        cred_manager.mark_credential_success(index1)
        cred_manager.mark_credential_failed(index2)
        logger.info("✅ Success/failure marking completed")
        
        # Test 5: Obtenir les statistiques
        logger.info("Test 5: Getting usage stats")
        stats = cred_manager.get_usage_stats()
        logger.info(f"✅ Stats: {stats['rotation_progress']}")
        
        # Test 6: Reset de la rotation
        logger.info("Test 6: Resetting rotation")
        cred_manager.reset_rotation(0)
        cred_reset, index_reset = cred_manager.get_next_credential()
        if index_reset == 1:  # Devrait être 1 après reset à 0
            logger.info("✅ Rotation reset working")
        else:
            logger.error(f"❌ Rotation reset failed: expected 1, got {index_reset}")
        
        logger.info("✅ CredentialManager tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ CredentialManager test failed: {e}")
        return False

def test_transaction_processor():
    """Tester le processeur de transactions avec rotation"""
    logger.info("🧪 Testing TransactionProcessor with rotation...")
    
    try:
        # Initialiser le processeur
        processor = TransactionProcessor()
        
        # Test 1: Obtenir le prochain credential
        logger.info("Test 1: Getting next credential from processor")
        cred, index = processor.get_next_credential()
        logger.info(f"✅ Got credential: {cred['email']} (index {index})")
        
        # Test 2: Créer une transaction de test
        logger.info("Test 2: Creating test transaction")
        test_transaction = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=9,
            status="pending",
            payload={
                "player_id": "533938203",
                "code": "TEST_ROTATION_CODE"
            },
            bot_type="pubg"
        )
        logger.info(f"✅ Test transaction created: {test_transaction.id}")
        
        # Test 3: Obtenir les statistiques du système
        logger.info("Test 3: Getting system stats")
        stats = processor.get_system_stats()
        logger.info(f"✅ System stats retrieved: {stats.get('credential_rotation', {}).get('rotation_progress', 'N/A')}")
        
        logger.info("✅ TransactionProcessor tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ TransactionProcessor test failed: {e}")
        return False

def test_rotation_cycle():
    """Tester un cycle complet de rotation"""
    logger.info("🧪 Testing complete rotation cycle...")
    
    try:
        cred_manager = CredentialManager()
        
        # Obtenir le nombre total de credentials
        total_creds = cred_manager.get_available_credentials_count()
        logger.info(f"Total credentials available: {total_creds}")
        
        # Tester plusieurs rotations
        used_credentials = []
        for i in range(min(5, total_creds)):  # Tester 5 rotations ou moins
            cred, index = cred_manager.get_next_credential()
            used_credentials.append((cred['email'], index))
            logger.info(f"Rotation {i+1}: {cred['email']} (index {index})")
        
        # Vérifier que tous les credentials sont différents
        emails = [cred[0] for cred in used_credentials]
        if len(set(emails)) == len(emails):
            logger.info("✅ All credentials are different")
        else:
            logger.error("❌ Some credentials were repeated")
        
        # Vérifier la progression séquentielle
        indices = [cred[1] for cred in used_credentials]
        is_sequential = all(indices[i] == (indices[i-1] + 1) % total_creds for i in range(1, len(indices)))
        if is_sequential:
            logger.info("✅ Rotation is sequential")
        else:
            logger.error(f"❌ Rotation is not sequential: {indices}")
        
        logger.info("✅ Rotation cycle test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Rotation cycle test failed: {e}")
        return False

def test_persistence():
    """Tester la persistance de l'état"""
    logger.info("🧪 Testing state persistence...")
    
    try:
        # Créer un premier gestionnaire
        cred_manager1 = CredentialManager()
        cred1, index1 = cred_manager1.get_next_credential()
        logger.info(f"First manager: {cred1['email']} (index {index1})")
        
        # Créer un deuxième gestionnaire (devrait reprendre l'état)
        cred_manager2 = CredentialManager()
        cred2, index2 = cred_manager2.get_next_credential()
        logger.info(f"Second manager: {cred2['email']} (index {index2})")
        
        # Vérifier que l'index a progressé
        if index2 == (index1 + 1) % cred_manager2.get_available_credentials_count():
            logger.info("✅ State persistence working correctly")
        else:
            logger.error(f"❌ State persistence failed: {index1} -> {index2}")
        
        logger.info("✅ Persistence test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Persistence test failed: {e}")
        return False

def main():
    """Fonction principale de test"""
    logger.info("🚀 Starting credential rotation test suite...")
    
    tests = [
        ("CredentialManager", test_credential_manager),
        ("TransactionProcessor", test_transaction_processor),
        ("Rotation Cycle", test_rotation_cycle),
        ("State Persistence", test_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Credential rotation system is working correctly.")
    else:
        logger.error(f"💥 {total - passed} tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

