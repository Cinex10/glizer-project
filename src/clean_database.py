#!/usr/bin/env python3
"""
Script pour nettoyer la base de données
Usage: python clean_database.py [options]
"""

import sys
import os
from sqlalchemy.orm import sessionmaker
from database import engine, get_db_session
from models import Transaction
from logging_config import get_logger

logger = get_logger(__name__)

def clean_all_transactions():
    """Supprimer toutes les transactions"""
    session = get_db_session()
    try:
        count = session.query(Transaction).count()
        session.query(Transaction).delete()
        session.commit()
        logger.info(f"Supprimé {count} transactions")
        return count
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def clean_failed_transactions():
    """Supprimer seulement les transactions échouées"""
    session = get_db_session()
    try:
        count = session.query(Transaction).filter(Transaction.status == "failed").count()
        session.query(Transaction).filter(Transaction.status == "failed").delete()
        session.commit()
        logger.info(f"Supprimé {count} transactions échouées")
        return count
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def clean_old_transactions(days=7):
    """Supprimer les transactions plus anciennes que X jours"""
    from datetime import datetime, timedelta
    session = get_db_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = session.query(Transaction).filter(Transaction.created_at < cutoff_date).count()
        session.query(Transaction).filter(Transaction.created_at < cutoff_date).delete()
        session.commit()
        logger.info(f"Supprimé {count} transactions plus anciennes que {days} jours")
        return count
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def show_stats():
    """Afficher les statistiques de la base"""
    session = get_db_session()
    try:
        total = session.query(Transaction).count()
        pending = session.query(Transaction).filter(Transaction.status == "pending").count()
        processing = session.query(Transaction).filter(Transaction.status == "processing").count()
        success = session.query(Transaction).filter(Transaction.status == "success").count()
        failed = session.query(Transaction).filter(Transaction.status == "failed").count()
        
        print(f"""
📊 Statistiques de la base de données:
   Total: {total}
   En attente: {pending}
   En cours: {processing}
   Réussies: {success}
   Échouées: {failed}
        """)
    finally:
        session.close()

def main():
    if len(sys.argv) < 2:
        print("""
🧹 Script de nettoyage de la base de données

Usage:
  python clean_database.py stats                    # Afficher les statistiques
  python clean_database.py clean-all               # Supprimer toutes les transactions
  python clean_database.py clean-failed            # Supprimer les transactions échouées
  python clean_database.py clean-old [jours]       # Supprimer les transactions > X jours (défaut: 7)
        """)
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        show_stats()
    elif command == "clean-all":
        confirm = input("⚠️  Êtes-vous sûr de vouloir supprimer TOUTES les transactions ? (oui/non): ")
        if confirm.lower() in ['oui', 'o', 'yes', 'y']:
            clean_all_transactions()
        else:
            print("Annulé.")
    elif command == "clean-failed":
        clean_failed_transactions()
    elif command == "clean-old":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        clean_old_transactions(days)
    else:
        print(f"Commande inconnue: {command}")

if __name__ == "__main__":
    main()

