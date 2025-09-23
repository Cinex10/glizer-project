#!/usr/bin/env python3
"""
Script pour ajouter des transactions dans la base de données PostgreSQL
pour tester le système Glizer Bot Processor
"""
import sys
import os
import uuid
from datetime import datetime
import json

# Ajouter le répertoire src au path
sys.path.append('src')

# Imports du projet
from src.database.postgresql import get_postgres_session
from src.database.models import BotTransaction

def add_test_transaction(bot_num, player_id, codes):
    """
    Ajouter une transaction de test dans la base
    
    Args:
        bot_num (int): Numéro du bot (9 ou 10)
        player_id (str): ID du joueur PUBG
        codes (list): Liste des codes de rédemption
    """
    
    # Générer un ID unique
    transaction_id = str(uuid.uuid4())
    
    # Créer le payload JSON
    payload = {
        "player_id": player_id,
        "codes": codes
    }
    
    # Obtenir une session de base de données
    db = get_postgres_session()
    
    try:
        # Créer la transaction
        transaction = BotTransaction(
            id=transaction_id,
            bot_num=bot_num,
            status="pending",
            payload=payload,
            bot_type="pubg",
            created_at=datetime.utcnow(),
            retry_count=0,
            max_retries=3
        )
        
        # Ajouter à la base
        db.add(transaction)
        db.commit()
        
        print(f"✅ Transaction ajoutée avec succès!")
        print(f"   ID: {transaction_id}")
        print(f"   Bot: {bot_num}")
        print(f"   Player ID: {player_id}")
        print(f"   Codes: {codes}")
        print(f"   Status: pending")
        
        return transaction_id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de l'ajout: {e}")
        return None
        
    finally:
        db.close()

def list_transactions():
    """Lister toutes les transactions"""
    
    db = get_postgres_session()
    
    try:
        transactions = db.query(BotTransaction).filter(
            BotTransaction.bot_num.in_([9, 10]),
            BotTransaction.bot_type == "pubg"
        ).order_by(BotTransaction.created_at.desc()).limit(20).all()
        
        if not transactions:
            print("📋 Aucune transaction trouvée")
            return
        
        print(f"📋 {len(transactions)} transactions trouvées:")
        print("-" * 80)
        
        for t in transactions:
            player_id = t.get_player_id() or "N/A"
            codes = t.get_redeem_codes() or []
            print(f"ID: {t.id[:8]}... | Bot: {t.bot_num} | Status: {t.status}")
            print(f"    Player: {player_id} | Codes: {len(codes)} | Created: {t.created_at}")
            if t.error_message:
                print(f"    Error: {t.error_message}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {e}")
        
    finally:
        db.close()

def main():
    """Menu principal"""
    
    if len(sys.argv) == 1:
        print("🤖 Gestionnaire de transactions Glizer Bot Processor")
        print()
        print("Usage:")
        print("  python3 add_transaction.py add <bot_num> <player_id> <codes>")
        print("  python3 add_transaction.py list")
        print("  python3 add_transaction.py example")
        print()
        print("Exemples:")
        print("  python3 add_transaction.py add 9 533938203 'CODE1,CODE2,CODE3'")
        print("  python3 add_transaction.py add 10 123456789 'TESTCODE123'")
        print("  python3 add_transaction.py list")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_transactions()
        
    elif command == "add":
        if len(sys.argv) < 5:
            print("❌ Arguments manquants pour 'add'")
            print("Usage: python3 add_transaction.py add <bot_num> <player_id> <codes>")
            return
            
        try:
            bot_num = int(sys.argv[2])
            player_id = sys.argv[3]
            codes_str = sys.argv[4]
            
            # Valider le bot_num
            if bot_num not in [9, 10]:
                print("❌ Le numéro de bot doit être 9 ou 10")
                return
            
            # Parser les codes
            codes = [code.strip() for code in codes_str.split(',')]
            
            # Ajouter la transaction
            add_test_transaction(bot_num, player_id, codes)
            
        except ValueError:
            print("❌ Le numéro de bot doit être un entier")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    elif command == "example":
        print("🎮 Ajout d'exemples de transactions...")
        
        # Exemple 1: Bot 9
        add_test_transaction(
            bot_num=9,
            player_id="533938203",
            codes=["TESTCODE1", "TESTCODE2"]
        )
        
        # Exemple 2: Bot 10  
        add_test_transaction(
            bot_num=10,
            player_id="987654321",
            codes=["EXAMPLE123", "DEMO456", "SAMPLE789"]
        )
        
        print("\n✅ Exemples ajoutés! Utilisez 'list' pour voir les transactions.")
        
    else:
        print(f"❌ Commande inconnue: {command}")

if __name__ == "__main__":
    main()
