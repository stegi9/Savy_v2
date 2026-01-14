"""
User Category model.
"""
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from db.database import Base
import uuid


class UserCategory(Base):
    __tablename__ = "user_categories"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50))
    color = Column(String(7))  # Hex color #RRGGBB
    category_type = Column(String(10), default="expense")  # 'expense' or 'income'
    budget_monthly = Column(Numeric(10, 2), nullable=True)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="categories")
    
    # Unique constraint: user can't have duplicate category names
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
