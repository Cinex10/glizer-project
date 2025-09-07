from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/transactions.db")

# Créer le moteur de base de données
engine = create_engine(DATABASE_URL, echo=False)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialiser la base de données et créer les tables"""
    # Créer le dossier data s'il n'existe pas
    os.makedirs("./data", exist_ok=True)
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Obtenir une session de base de données"""
    return SessionLocal()

def get_db():
    """Générateur de session pour FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


