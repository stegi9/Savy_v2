"""
Partner model (for optimization providers).
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.mysql import CHAR
from db.database import Base
import uuid


class Partner(Base):
    __tablename__ = "partners"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # 'energy', 'telco', 'insurance'
    description = Column(Text, nullable=True)
    affiliate_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
