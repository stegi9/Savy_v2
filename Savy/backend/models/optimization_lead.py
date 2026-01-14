"""
Optimization Lead model.
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class OptimizationLead(Base):
    __tablename__ = "optimization_leads"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    bill_id = Column(CHAR(36), ForeignKey("recurring_bills.id", ondelete="CASCADE"), nullable=True)
    bill_category = Column(String(100), nullable=True)
    current_cost = Column(Numeric(10, 2), nullable=True)
    optimized_cost = Column(Numeric(10, 2), nullable=True)
    savings_amount = Column(Numeric(10, 2), nullable=True)
    partner_name = Column(String(255), nullable=True)
    partner_offer_details = Column(String(500), nullable=True)
    status = Column(String(50), default="pending")  # 'pending', 'accepted', 'rejected'
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="optimization_leads")
    bill = relationship("RecurringBill", back_populates="optimization_leads")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
