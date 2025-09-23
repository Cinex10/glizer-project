"""
Modèles adaptés pour la table bots_transactions PostgreSQL
Architecture simplifiée selon les spécifications Salla
"""
from sqlalchemy import Column, String, Integer, JSON, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BotTransaction(Base):
    """
    Modèle pour la table bots_transactions selon les spécifications Salla
    Colonnes : id, bot_num, status, payload, bot_type
    """
    __tablename__ = "bots_transactions"
    
    id = Column(String, primary_key=True)
    bot_num = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, success, failure
    payload = Column(JSON)  # JSON avec player_id, code, email, password
    bot_type = Column(String, nullable=False)
    
    # Contraintes de validation
    __table_args__ = (
        CheckConstraint('bot_num >= 1 AND bot_num <= 10', name='check_bot_num_range'),
        CheckConstraint("bot_type IN ('yalla_ludo', 'pubg')", name='check_bot_type_valid'),
    )
    
    def __repr__(self):
        return f"<BotTransaction(id={self.id}, bot_num={self.bot_num}, status={self.status}, bot_type={self.bot_type})>"
    
    def get_player_id(self):
        """Extraire le player_id du payload JSON"""
        if self.payload and isinstance(self.payload, dict):
            return self.payload.get('player_id')
        return None
    
    def get_code(self):
        """Extraire le code de rédemption du payload JSON"""
        if self.payload and isinstance(self.payload, dict):
            return self.payload.get('code')
        return None
    
    def get_email(self):
        """Extraire l'email du payload JSON"""
        if self.payload and isinstance(self.payload, dict):
            return self.payload.get('email')
        return None
    
    def get_password(self):
        """Extraire le password du payload JSON"""
        if self.payload and isinstance(self.payload, dict):
            return self.payload.get('password')
        return None
    
    def is_pubg_bot(self):
        """Vérifier si c'est un bot PUBG"""
        return self.bot_type == "pubg"
    
    def is_yalla_ludo_bot(self):
        """Vérifier si c'est un bot Yalla Ludo"""
        return self.bot_type == "yalla_ludo"
    
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

