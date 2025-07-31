from sqlalchemy import Column, String, Text, Integer

from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    order_type = Column(String, index=True)  # e.g., "yalla_ludo"
    order_payload = Column(Text)  # JSON string of the order data
    remaining_retries = Column(Integer, default=3)  # Number of retries left 