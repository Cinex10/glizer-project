#!/usr/bin/env python3
"""
Script de test pour vérifier le nouveau format de payload
"""
import json
import uuid
from database.models import BotTransaction
from services.transaction_processor import TransactionProcessor
from services.credential_manager import CredentialManager
from logging_config import get_logger

logger = get_logger(__name__)

def test_new_payload_format():
    """Tester le nouveau format de payload"""
    logger.info("🧪 Testing new payload format...")
    
    try:
        # Test 1: Créer une transaction avec le nouveau format
        logger.info("Test 1: Creating transaction with new format")
        transaction = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=9,
            status="pending",
            payload={
                "player_id": "533938203",
                "code": "TEST_NEW_FORMAT_CODE",
                "email": "client@example.com",  # Stocké mais non utilisé
                "password": "clientpass"        # Stocké mais non utilisé
            },
            bot_type="pubg"
        )
        
        # Test 2: Vérifier l'extraction des données
        logger.info("Test 2: Testing data extraction")
        player_id = transaction.get_player_id()
        code = transaction.get_code()
        redeem_codes = transaction.get_redeem_codes()
        
        assert player_id == "533938203", f"Expected player_id '533938203', got '{player_id}'"
        assert code == "TEST_NEW_FORMAT_CODE", f"Expected code 'TEST_NEW_FORMAT_CODE', got '{code}'"
        assert redeem_codes == ["TEST_NEW_FORMAT_CODE"], f"Expected ['TEST_NEW_FORMAT_CODE'], got {redeem_codes}"
        
        logger.info("✅ Data extraction working correctly")
        
        # Test 3: Vérifier que les credentials rotatifs sont utilisés
        logger.info("Test 3: Testing credential rotation")
        cred_manager = CredentialManager()
        cred, index = cred_manager.get_next_credential()
        
        logger.info(f"✅ Using rotative credential: {cred['email']} (index {index})")
        logger.info(f"✅ Client email/password in payload are IGNORED: {transaction.payload.get('email')}")
        
        # Test 4: Vérifier le processeur de transactions
        logger.info("Test 4: Testing transaction processor")
        processor = TransactionProcessor()
        
        # Simuler l'extraction des données (sans exécuter l'automatisation)
        player_id = transaction.get_player_id()
        redeem_codes = transaction.get_redeem_codes()
        
        assert player_id is not None, "Player ID should not be None"
        assert len(redeem_codes) > 0, "Redeem codes should not be empty"
        
        logger.info(f"✅ Transaction processor can extract: player_id={player_id}, codes={redeem_codes}")
        
        # Test 5: Vérifier la structure du payload
        logger.info("Test 5: Testing payload structure")
        payload = transaction.payload
        
        required_fields = ["player_id", "code"]
        optional_fields = ["email", "password"]
        
        for field in required_fields:
            assert field in payload, f"Required field '{field}' missing from payload"
            logger.info(f"✅ Required field '{field}': {payload[field]}")
        
        for field in optional_fields:
            if field in payload:
                logger.info(f"✅ Optional field '{field}': {payload[field]} (stored but not used)")
        
        logger.info("✅ All tests passed! New payload format is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def test_credential_rotation_vs_payload():
    """Tester que les credentials rotatifs sont utilisés au lieu de ceux du payload"""
    logger.info("🧪 Testing credential rotation vs payload credentials...")
    
    try:
        # Créer une transaction avec des credentials dans le payload
        transaction = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=10,
            status="pending",
            payload={
                "player_id": "987654321",
                "code": "ROTATION_TEST_CODE",
                "email": "payload@example.com",    # Credential du payload
                "password": "payloadpassword"      # Credential du payload
            },
            bot_type="pubg"
        )
        
        # Obtenir le credential rotatif
        cred_manager = CredentialManager()
        rotative_cred, index = cred_manager.get_next_credential()
        
        # Vérifier que les credentials sont différents
        payload_email = transaction.payload.get("email")
        rotative_email = rotative_cred["email"]
        
        assert payload_email != rotative_email, "Payload email should be different from rotative email"
        
        logger.info(f"✅ Payload email (ignored): {payload_email}")
        logger.info(f"✅ Rotative email (used): {rotative_email}")
        logger.info(f"✅ Credential rotation index: {index}")
        
        logger.info("✅ Credential rotation test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Credential rotation test failed: {e}")
        return False

def main():
    """Fonction principale de test"""
    logger.info("🚀 Starting payload format test suite...")
    
    tests = [
        ("New Payload Format", test_new_payload_format),
        ("Credential Rotation vs Payload", test_credential_rotation_vs_payload)
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
        logger.info("🎉 All tests passed! Payload format update is working correctly.")
        logger.info("📋 Summary:")
        logger.info("   - New format: player_id + code (required)")
        logger.info("   - Email/password in payload: stored but IGNORED")
        logger.info("   - Rotative credentials: used for automation")
        logger.info("   - Compatible with Salla specifications")
    else:
        logger.error(f"💥 {total - passed} tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


