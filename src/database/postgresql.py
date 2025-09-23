"""
Configuration PostgreSQL pour la connexion à la base externe
"""
import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)

# Configuration de la base PostgreSQL externe
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "glizer_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "glizer_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "glizer_pass")

# URL de connexion PostgreSQL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

class PostgreSQLManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialiser la connexion PostgreSQL"""
        try:
            logger.info(f"Connecting to PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
            
            # Configuration du moteur avec pool de connexions
            self.engine = create_engine(
                DATABASE_URL,
                poolclass=NullPool,  # Pas de pool pour éviter les problèmes de connexion
                echo=False,
                pool_pre_ping=True,  # Vérifier les connexions avant utilisation
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "glizer_bot_processor"
                }
            )
            
            # Créer la session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Tester la connexion
            self._test_connection()
            logger.info("PostgreSQL connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise Exception(f"PostgreSQL connection failed: {e}")
    
    def _test_connection(self):
        """Tester la connexion à la base"""
        session = self.SessionLocal()
        try:
            # Exécuter une requête simple pour tester
            result = session.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            if test_value != 1:
                raise Exception("Connection test failed")
            logger.info("PostgreSQL connection test successful")
        except Exception as e:
            logger.error(f"PostgreSQL connection test failed: {e}")
            raise
        finally:
            session.close()
    
    def get_session(self):
        """Obtenir une session de base de données"""
        return self.SessionLocal()
    
    def close(self):
        """Fermer la connexion"""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL connection closed")

# Instance globale du gestionnaire PostgreSQL
postgres_manager = PostgreSQLManager()

def get_postgres_session():
    """Obtenir une session PostgreSQL"""
    return postgres_manager.get_session()

def get_postgres_engine():
    """Obtenir le moteur PostgreSQL"""
    return postgres_manager.engine

def close_postgres_connection():
    """Fermer la connexion PostgreSQL"""
    postgres_manager.close()

