"""
Affiliate Advisor Models (V3.1 Spec)
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, Text, JSON, Enum as SQLEnum, DECIMAL, CHAR, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import enum

# Enums
class PlacementType(str, enum.Enum):
    DASHBOARD = "DASHBOARD"
    HUB = "HUB"
    CHAT = "CHAT"

class OfferStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class MatchType(str, enum.Enum):
    EXACT = "EXACT"
    PREFIX = "PREFIX"
    REGEX = "REGEX"
    MCC = "MCC"

class InteractionType(str, enum.Enum):
    IMPRESSION = "IMPRESSION"
    CLICK = "CLICK"
    DISMISS = "DISMISS"
    CONVERSION = "CONVERSION"

class AffiliatePartner(Base):
    __tablename__ = "affiliate_partners"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=True)
    trust_score = Column(Integer, default=80)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    offers = relationship("AffiliateOffer", back_populates="partner")
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class AffiliateOffer(Base):
    __tablename__ = "affiliate_offers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    partner_id = Column(Integer, ForeignKey("affiliate_partners.id"), nullable=False)
    status = Column(SQLEnum(OfferStatus), default=OfferStatus.DRAFT)
    
    # Content
    title = Column(String(150), nullable=False)
    copy_text = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    target_link_template = Column(String(500), nullable=False)
    
    # Targeting
    target_country = Column(CHAR(2), default="IT")
    currency = Column(CHAR(3), default="EUR")
    min_amount = Column(DECIMAL(10, 2), default=0.00)
    
    # Policy
    priority = Column(Integer, default=0)
    cooldown_hours = Column(Integer, default=72)
    max_impressions_7d = Column(Integer, default=3)
    requires_opt_in = Column(Boolean, default=False)
    
    # Validity
    published_at = Column(DateTime, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)

    # Relationships
    partner = relationship("AffiliatePartner", back_populates="offers")
    triggers = relationship("OfferTrigger", back_populates="offer")
    search_terms = relationship("OfferSearchTerm", back_populates="offer")
    
    __table_args__ = (
        Index('idx_status_validity', 'status', 'valid_until'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class OfferTrigger(Base):
    __tablename__ = "offer_triggers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(Integer, ForeignKey("affiliate_offers.id"), nullable=False)
    
    match_type = Column(SQLEnum(MatchType), nullable=False)
    
    # Pattern columns for efficient indexing
    pattern_text = Column(String(255), nullable=True) # For EXACT, PREFIX
    pattern_mcc = Column(Integer, nullable=True)      # For MCC
    pattern_regex = Column(String(255), nullable=True) # For REGEX (not indexed usually)
    
    priority = Column(Integer, default=0)
    
    offer = relationship("AffiliateOffer", back_populates="triggers")
    
    __table_args__ = (
        Index('idx_exact', 'match_type', 'pattern_text'),
        Index('idx_mcc', 'match_type', 'pattern_mcc'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class OfferSearchTerm(Base):
    __tablename__ = "offer_search_terms"
    
    offer_id = Column(Integer, ForeignKey("affiliate_offers.id"), primary_key=True)
    term = Column(String(100), primary_key=True)
    
    offer = relationship("AffiliateOffer", back_populates="search_terms")
    
    __table_args__ = (
        Index('idx_fulltext_term', 'term', mysql_prefix='FULLTEXT'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class UserPlacementState(Base):
    """Denormalized state for Global Capping"""
    __tablename__ = "user_placement_state"
    
    user_id = Column(CHAR(36), primary_key=True)
    placement = Column(SQLEnum(PlacementType), primary_key=True)
    last_impression_at = Column(DateTime, nullable=True)
    impressions_24h = Column(Integer, default=0)
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class UserOfferState(Base):
    """Denormalized state for Offer Capping & Cooldown"""
    __tablename__ = "user_offer_state"
    
    user_id = Column(CHAR(36), primary_key=True)
    offer_id = Column(Integer, primary_key=True)
    
    first_seen_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    impressions_7d = Column(Integer, default=0)
    
    is_dismissed = Column(Boolean, default=False)
    dismissed_until = Column(DateTime, nullable=True)
    
    is_converted = Column(Boolean, default=False)
    
    __table_args__ = (
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class UserRecommendation(Base):
    """Persistent Cache of Computed Recommendations"""
    __tablename__ = "user_recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(CHAR(32), unique=True, nullable=False) # UUID4 Hex
    user_id = Column(CHAR(36), nullable=False)
    offer_id = Column(Integer, nullable=False)
    placement = Column(SQLEnum(PlacementType), nullable=False)
    
    score = Column(Float, default=0.0)
    reason_code = Column(String(50), nullable=True)
    
    # Security
    token_hash = Column(CHAR(64), nullable=False) # SHA256
    expires_at = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_user_dashboard', 'user_id', 'placement', 'expires_at'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )

class AffiliateInteraction(Base):
    """Audit Log"""
    __tablename__ = "affiliate_interactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(CHAR(36), nullable=False)
    recommendation_id = Column(Integer, nullable=True)
    offer_id = Column(Integer, nullable=False)
    
    event_type = Column(SQLEnum(InteractionType), nullable=False)
    placement = Column(SQLEnum(PlacementType), nullable=True)
    ab_variant = Column(String(20), default="CONTROL")
    
    idempotency_key = Column(CHAR(36), nullable=True)
    
    __table_args__ = (
        # Composite unique key for Robust Idempotency (User requested)
        Index('idx_idempotency', 'user_id', 'idempotency_key', unique=True),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'},
    )
