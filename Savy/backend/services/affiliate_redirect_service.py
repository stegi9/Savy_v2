"""
Affiliate Redirect Service.
Handles secure token generation and URL resolution.
"""
import hashlib
import secrets
import structlog
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.affiliate import (
    UserRecommendation, 
    AffiliateOffer, 
    AffiliatePartner, 
    AffiliateInteraction, 
    InteractionType, 
    PlacementType,
    OfferStatus
)

logger = structlog.get_logger()

class AffiliateRedirectService:
    def __init__(self, db: Session):
        self.db = db

    def generate_token(self, user_id: str, offer_id: int, placement: PlacementType, score: float = 0.0, reason_code: str = None) -> Tuple[str, str]:
        """
        Generates a secure redirect token and persists the recommendation.
        Returns: (raw_token, public_id)
        """
        # 1. Generate opaque token (client-facing)
        raw_token = secrets.token_urlsafe(32) # 32 bytes approx 43 chars
        
        # 2. Hash it (server-storage)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        # 3. Generate public_id for tracking
        public_id = secrets.token_hex(16)
        
        # 4. Expiration (e.g. 2 hours)
        expires_at = datetime.utcnow() + timedelta(hours=2)
        
        # 5. Persist
        recommendation = UserRecommendation(
            public_id=public_id,
            user_id=user_id,
            offer_id=offer_id,
            placement=placement,
            score=score,
            reason_code=reason_code,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.db.add(recommendation)
        self.db.commit()
        
        return raw_token, public_id

    def resolve_token(self, raw_token: str, user_agent: str = None, ip_address: str = None) -> Optional[str]:
        """
        Validates token and returns target URL.
        Logs CLICK interaction.
        Returns None if invalid/expired/gone.
        """
        # 1. Hash incoming token
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        # 2. Lookup Recommendation
        stmt = select(UserRecommendation).where(UserRecommendation.token_hash == token_hash)
        recommendation = self.db.execute(stmt).scalars().first()
        
        if not recommendation:
            logger.warning("affiliate_token_not_found", token_hash=token_hash[:8])
            return None
            
        # 3. Validate Expiration
        if recommendation.expires_at < datetime.utcnow():
            logger.info("affiliate_token_expired", public_id=recommendation.public_id)
            return None
            
        # 4. Load Offer & Partner
        offer = self.db.get(AffiliateOffer, recommendation.offer_id)
        if not offer or offer.status != OfferStatus.PUBLISHED:
            logger.info("affiliate_offer_unavailable", offer_id=recommendation.offer_id)
            return None
            
        partner = self.db.get(AffiliatePartner, offer.partner_id)
        if not partner or not partner.is_active:
            logger.info("affiliate_partner_inactive", partner_id=offer.partner_id)
            return None

        # 5. Generate Sub-ID (Anonymous Click ID)
        # Format: click_{public_id}_{timestamp_hex}
        ts_hex = hex(int(datetime.utcnow().timestamp()))[2:]
        sub_id = f"click_{recommendation.public_id}_{ts_hex}"
        
        # 6. Build Target URL
        # Template expected: "https://partner.com/?ref={sub_id}"
        try:
            target_url = offer.target_link_template.format(
                sub_id=sub_id,
                user_id="ANON", # Explicitly block user_id leakage
                offer_id=offer.id
            )
        except Exception as e:
            logger.error("affiliate_url_build_failed", error=str(e))
            # Fallback to raw template if format fails (safety) but might break tracking
            target_url = offer.target_link_template
            
        # 7. Log Interaction (Async-ish: here sync for MVP, ideally queued)
        self._log_click(recommendation, user_agent)
        
        return target_url

    def _log_click(self, rec: UserRecommendation, user_agent: str):
        """Logs the click interaction."""
        try:
            interaction = AffiliateInteraction(
                user_id=rec.user_id,
                recommendation_id=rec.id,
                offer_id=rec.offer_id,
                event_type=InteractionType.CLICK,
                placement=rec.placement,
                idempotency_key=f"click_{rec.public_id}" # One click per rec generation usually
            )
            self.db.add(interaction)
            self.db.commit()
        except Exception as e:
            logger.error("affiliate_click_log_failed", error=str(e))
            self.db.rollback()
