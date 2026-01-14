"""
Recurring Bill model.
"""
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class RecurringBill(Base):
    __tablename__ = "recurring_bills"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    due_day = Column(Integer, nullable=True)  # Day of month (1-31)
    category = Column(String(100), nullable=True)  # 'energy', 'telco', 'rent', etc.
    provider = Column(String(255), nullable=True)  # Current provider name
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recurring_bills")
    optimization_leads = relationship("OptimizationLead", back_populates="bill", cascade="all, delete-orphan")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
