"""
User model (profiles table).
"""
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, func, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class User(Base):
    __tablename__ = "profiles"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)  # For authentication
    hashed_password = Column(String(255), nullable=False)  # Bcrypt hash
    full_name = Column(String(255), nullable=False)
    current_balance = Column(Numeric(10, 2), default=0.00)
    monthly_budget = Column(Numeric(10, 2), default=2000.00)  # Global monthly budget
    currency = Column(String(3), default="EUR")
    # Notification settings
    budget_notifications = Column(Boolean, default=True)
    ai_tips_enabled = Column(Boolean, default=True)
    optimization_alerts = Column(Boolean, default=True)
    saltedge_customer_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    categories = relationship("UserCategory", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    recurring_bills = relationship("RecurringBill", back_populates="user", cascade="all, delete-orphan")
    optimization_leads = relationship("OptimizationLead", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
