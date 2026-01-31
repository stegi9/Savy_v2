"""
SQLAlchemy model for Refresh Tokens.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from db.database import Base
import uuid


class RefreshToken(Base):
    """Refresh token model for JWT token renewal."""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(CHAR(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="refresh_tokens")
    
    def is_valid(self) -> bool:
        """Check if token is still valid (not expired and not revoked)."""
        return not self.is_revoked and self.expires_at > datetime.utcnow()
    
    def revoke(self):
        """Revoke the refresh token."""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
