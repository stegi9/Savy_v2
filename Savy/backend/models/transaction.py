"""
Transaction model.
"""
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, Text, Float, func, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_account_id = Column(CHAR(36), ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True)
    provider_transaction_id = Column(String(100), nullable=True)
    category_id = Column(CHAR(36), ForeignKey("user_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    transaction_type = Column(String(20), default="expense")  # "expense" or "income"
    category = Column(String(100), nullable=True)  # Kept for legacy/fallback
    subcategory = Column(String(100), nullable=True)
    merchant = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    transaction_date = Column(Date, nullable=False)
    
    # AI Categorization fields
    ai_confidence = Column(Float, nullable=True)
    ai_context = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    needs_review = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category_rel = relationship("UserCategory", backref="transactions")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )


class MerchantRule(Base):
    """
    Stores user corrections for merchant categorization.
    When a user corrects a category, we save the rule to use next time.
    """
    __tablename__ = "merchant_rules"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(CHAR(36), ForeignKey("user_categories.id", ondelete="CASCADE"), nullable=False)
    merchant_pattern = Column(String(255), nullable=False)  # Lowercase merchant name
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    category = relationship("UserCategory")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
