"""
Background Job Model for DB Queue Fallback.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from db.database import Base

class BackgroundJob(Base):
    __tablename__ = "background_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    queue_name = Column(String(50), default="default")
    task_name = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    
    status = Column(String(20), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    result = Column(Text, nullable=True) # Error message or result summary
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
