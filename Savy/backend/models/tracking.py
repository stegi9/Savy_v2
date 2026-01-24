from sqlalchemy import Column, Integer, String, DateTime, Numeric, JSON, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
import uuid

class AffiliateClickToken(Base):
    __tablename__ = "affiliate_click_tokens"

    token = Column(String(64), primary_key=True, index=True) # Secure random token
    provider = Column(String(50), nullable=False)
    offer_id = Column(String(100), nullable=False)
    vertical = Column(String(50), nullable=False)
    user_id_hash = Column(String(64), nullable=False) # Or user_id if internal
    payload_min = Column(JSON, nullable=True) # Minimal reconstruction data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

class AffiliateClickEvent(Base):
    __tablename__ = "affiliate_click_events"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), ForeignKey("affiliate_click_tokens.token"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id_hash = Column(String(64), nullable=False)
    vertical = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    metadata_min = Column(JSON, nullable=True) # IP, UA, Referer

class AffiliateConversion(Base):
    __tablename__ = "affiliate_conversions"

    id = Column(Integer, primary_key=True, index=True)
    sub_id = Column(String(64), nullable=False, index=True) # The tracking ID we sent
    network = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="EUR")
    status = Column(String(20), nullable=False) # approved, pending
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    raw_payload = Column(JSON, nullable=True)
