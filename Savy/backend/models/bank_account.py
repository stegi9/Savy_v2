from sqlalchemy import Column, String, ForeignKey, DateTime, DECIMAL, func
from sqlalchemy.orm import relationship
import uuid
from db.database import Base

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String(36), ForeignKey("bank_connections.id", ondelete="CASCADE"), nullable=False)
    provider_account_id = Column(String(100), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    currency = Column(String(3), default="EUR")
    balance = Column(DECIMAL(10, 2), nullable=True)
    nature = Column(String(50), nullable=True) # account, card, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    connection = relationship("BankConnection", backref="accounts")

    def __repr__(self):
        return f"<BankAccount(id={self.id}, name={self.name}, currency={self.currency})>"
