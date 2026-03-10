from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL, Boolean, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
import uuid
from db.database import Base

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    connection_id = Column(String(36), ForeignKey("bank_connections.id", ondelete="CASCADE"), nullable=True) # Open Banking ID
    is_manual = Column(Boolean, default=False)
    
    provider_account_id = Column(String(100), unique=True, nullable=True) # SaltEdge provider ID
    name = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True) # HEX code like #FF0000
    icon = Column(String(50), nullable=True) # Material Icon name
    
    currency = Column(String(3), default="EUR")
    balance = Column(DECIMAL(10, 2), nullable=True)
    nature = Column(String(50), nullable=True) # account, card, cash, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    connection = relationship("BankConnection", backref="accounts")
    user = relationship("User", back_populates="accounts")

    def __repr__(self):
        return f"<BankAccount(id={self.id}, name={self.name}, is_manual={self.is_manual})>"
