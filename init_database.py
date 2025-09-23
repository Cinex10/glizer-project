#!/usr/bin/env python3
"""
Script pour initialiser la base de données PostgreSQL
Crée les tables nécessaires pour le Glizer Bot Processor
"""
import sys
import os

# Ajouter le répertoire src au path
sys.path.append('src')

from src.database.postgresql import get_postgres_engine
from src.database.models import Base
import uuid
from datetime import datetime

def create_tables():
    """Créer toutes les tables"""
    
    try:
        engine = get_postgres_engine()
        
        print("🔧 Création des tables...")
        
        # Créer toutes les tables définies dans les modèles
        Base.metadata.create_all(engine)
        
        print("✅ Tables créées avec succès!")
        
        # Vérifier que la table existe
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'bots_transactions'
            """))
            
            if result.fetchone():
                print("✅ Table 'bots_transactions' confirmée")
            else:
                print("❌ Table 'bots_transactions' non trouvée")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False

def add_sample_data():
    """Ajouter des données d'exemple"""
    
    try:
        from src.database.postgresql import get_postgres_session
        from src.database.models import BotTransaction
        
        db = get_postgres_session()
        
        # Vérifier si des données existent déjà
        existing = db.query(BotTransaction).first()
        if existing:
            print("⚠️  Des données existent déjà, pas d'ajout d'exemples")
            db.close()
            return
        
        print("📝 Ajout de données d'exemple...")
        
        # Transaction pour bot 9
        transaction1 = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=9,
            status="pending",
            payload={
                "player_id": "533938203",
                "codes": ["TESTCODE1", "TESTCODE2"]
            },
            bot_type="pubg"
        )
        
        # Transaction pour bot 10
        transaction2 = BotTransaction(
            id=str(uuid.uuid4()),
            bot_num=10,
            status="pending",
            payload={
                "player_id": "987654321",
                "codes": ["EXAMPLE123", "DEMO456"]
            },
            bot_type="pubg"
        )
        
        db.add(transaction1)
        db.add(transaction2)
        db.commit()
        
        print("✅ Données d'exemple ajoutées:")
        print(f"   - Transaction bot 9: {transaction1.id}")
        print(f"   - Transaction bot 10: {transaction2.id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des données: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🚀 Initialisation de la base de données Glizer Bot Processor")
    print("=" * 60)
    
    # Créer les tables
    if not create_tables():
        print("❌ Échec de la création des tables")
        sys.exit(1)
    
    # Demander si on veut ajouter des exemples
    if len(sys.argv) > 1 and sys.argv[1] == "--with-samples":
        add_sample_data()
    
    print("=" * 60)
    print("🎉 Initialisation terminée!")
    print()
    print("Pour ajouter des transactions:")
    print("  python3 add_transaction.py add 9 533938203 'CODE1,CODE2'")
    print("  python3 add_transaction.py list")

if __name__ == "__main__":
    main()









