"""
Modèles adaptés pour la table bots_transactions PostgreSQL
Architecture adaptée à la structure réelle de la base de données
"""
from sqlalchemy import Column, String, Integer, JSON, DateTime, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BotTransaction(Base):
    """
    Modèle pour la table bots_transactions selon la structure réelle
    Colonnes : id, bot, bot_num, status, payloads, f_u, created_at, updated_at, deleted_at, failure_reason, payload
    """
    __tablename__ = "bots_transactions"
    
    id = Column(String, primary_key=True)
    bot = Column(String)  # Nouvelle colonne bot
    bot_num = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, success, failure
    payloads = Column(JSON)  # JSON avec player_id, code, email, password (ancien payload)
    f_u = Column(String)  # Nouvelle colonne f_u
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    failure_reason = Column(String)  # wrong_player_id, wrong_code, wrong_item_type, wrong_amount, wrong_email_password, other
    payload = Column(JSON)  # Nouvelle colonne payload
    
    # Contraintes de validation
    __table_args__ = (
        CheckConstraint('bot_num >= 1 AND bot_num <= 10', name='check_bot_num_range'),
        CheckConstraint("bot IN ('yalla_ludo', 'pubg')", name='check_bot_valid'),
    )
    
    def __repr__(self):
        return f"<BotTransaction(id={self.id}, bot_num={self.bot_num}, status={self.status}, bot={self.bot})>"
    
    def get_player_id(self):
        """Extraire le player_id du payload JSON (utilise payloads)"""
        if self.payloads and isinstance(self.payloads, dict):
            return self.payloads.get('player_id')
        return None
    
    def get_code(self):
        """Extraire le code de rédemption du payload JSON (utilise payloads)"""
        if self.payloads and isinstance(self.payloads, dict):
            return self.payloads.get('code')
        return None
    
    def get_redeem_codes(self):
        """Extraire les codes de rédemption du payload JSON (compatibilité)"""
        code = self.get_code()
        return [code] if code else []
    
    def get_email(self):
        """Extraire l'email du payload JSON (utilise payloads)"""
        if self.payloads and isinstance(self.payloads, dict):
            return self.payloads.get('email')
        return None
    
    def get_password(self):
        """Extraire le password du payload JSON (utilise payloads)"""
        if self.payloads and isinstance(self.payloads, dict):
            return self.payloads.get('password')
        return None
    
    def is_pubg_bot(self):
        """Vérifier si c'est un bot PUBG (utilise la colonne bot)"""
        return self.bot == "pubg"
    
    def is_yalla_ludo_bot(self):
        """Vérifier si c'est un bot Yalla Ludo (utilise la colonne bot)"""
        return self.bot == "yalla_ludo"
    
    def is_pending(self):
        """Vérifier si la transaction est en attente"""
        return self.status == "pending"
    
    def is_success(self):
        """Vérifier si la transaction a réussi"""
        return self.status == "success"
    
    def is_failure(self):
        """Vérifier si la transaction a échoué"""
        return self.status == "failure"

# Note: BotStats supprimé car non requis dans les spécifications Salla
# La table bots_transactions est maintenant simplifiée avec seulement les colonnes essentielles

