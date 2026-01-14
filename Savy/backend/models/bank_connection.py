from sqlalchemy import Column, String, ForeignKey, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from db.database import Base

class BankConnectionStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    LINKED = "LINKED"
    EXPIRED = "EXPIRED"
    EERROR = "ERROR"

class BankConnection(Base):
    __tablename__ = "bank_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False)
    connection_id = Column(String(100), unique=True, nullable=True) # Salt Edge Connection ID
    provider_code = Column(String(50), nullable=True)
    status = Column(String(20), default="active")
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="bank_connections")

    def __repr__(self):
        return f"<BankConnection(id={self.id}, user_id={self.user_id}, status={self.status})>"
