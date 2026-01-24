"""
Affiliate Matching Engine.
Core logic for analyzing transactions and generating recommendations.
"""
import structlog
from typing import List, Dict, Set, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from models.transaction import Transaction
from models.affiliate import (
    AffiliateOffer, 
    OfferTrigger, 
    MatchType, 
    OfferStatus, 
    UserOfferState, 
    UserPlacementState,
    PlacementType
)
from services.merchant_normalization_service import MerchantNormalizationService
from services.affiliate_redirect_service import AffiliateRedirectService

logger = structlog.get_logger()

class AffiliateMatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.normalizer = MerchantNormalizationService()
        self.redirect_service = AffiliateRedirectService(db)
        
    def process_user_transactions(self, user_id: str, transaction_ids: List[str]):
        """
        Main entry point. Analyzes new transactions and generates recommendations.
        """
        logger.info("affiliate_matching_start", user_id=user_id, tx_count=len(transaction_ids))
        
        # 0. Global Cap Check (Dashboard)
        # Check if user already saw a dashboard card in last 24h
        stmt = select(UserPlacementState).where(
            UserPlacementState.user_id == user_id,
            UserPlacementState.placement == PlacementType.DASHBOARD
        )
        placement_state = self.db.execute(stmt).scalars().first()
        
        if placement_state and placement_state.last_impression_at:
             if placement_state.last_impression_at > datetime.utcnow() - timedelta(hours=24):
                 logger.info("affiliate_global_cap_hit", user_id=user_id)
                 return # Stop processing to save resources (or continue for HUB placement?)
                 # For MVP we stop. In future we might calculate for HUB anyway.

        # 1. Fetch Transactions
        # Fetch only the ones triggered
        txs = self.db.query(Transaction).filter(Transaction.id.in_(transaction_ids)).all()
        if not txs:
            return

        # 2. Candidate Retrieval (Hybrid)
        candidates = self._find_candidates(txs)
        
        if not candidates:
            return

        # 3. Eligibility & Scoring
        best_offer = None
        best_score = -1.0
        best_reason = None
        
        for offer, reason_code, source_tx in candidates:
            # 3.1 Hard Constraints
            if not self._check_eligibility(offer, source_tx):
                continue
                
            # 3.2 Policy Check (Cap/Cooldown)
            if not self._check_policy(user_id, offer):
                continue
                
            # 3.3 Scoring
            score = self._calculate_score(offer, source_tx)
            
            # Tie-break
            if score > best_score:
                best_score = score
                best_offer = offer
                best_reason = reason_code
            elif score == best_score and best_offer:
                # Tie-break logic: TrustScore or ID
                if offer.partner.trust_score > best_offer.partner.trust_score:
                    best_offer = offer
                    best_reason = reason_code
        
        # 4. Persistence
        if best_offer:
            logger.info("affiliate_recommendation_found", user_id=user_id, offer_id=best_offer.id)
            self.redirect_service.generate_token(
                user_id=user_id,
                offer_id=best_offer.id,
                placement=PlacementType.DASHBOARD,
                score=best_score,
                reason_code=best_reason
            )

    def _find_candidates(self, txs: List[Transaction]) -> List[Tuple[AffiliateOffer, str, Transaction]]:
        """
        Returns list of (Offer, ReasonCode, TriggerTransaction).
        Hybrid Strategy: DB Index + Memory Scan.
        """
        candidates = []
        normalized_merchants = {} # Cache normalization
        
        # Pre-load active offers and triggers (Assumption: DB < 500 active offers)
        # In a larger system, this would be specific queries.
        active_triggers = self.db.query(OfferTrigger).join(AffiliateOffer).filter(
            AffiliateOffer.status == OfferStatus.PUBLISHED
        ).all()
        
        # Partition triggers for efficiency
        triggers_exact = {} 
        triggers_prefix = []
        triggers_regex = []
        triggers_mcc = {}
        
        for t in active_triggers:
            if t.match_type == MatchType.EXACT:
                k = t.pattern_text.upper()
                if k not in triggers_exact: triggers_exact[k] = []
                triggers_exact[k].append(t)
            elif t.match_type == MatchType.PREFIX:
                triggers_prefix.append(t)
            elif t.match_type == MatchType.MCC:
                 if t.pattern_mcc not in triggers_mcc: triggers_mcc[t.pattern_mcc] = []
                 triggers_mcc[t.pattern_mcc].append(t)
        
        print(f"[DEBUG] Triggers loaded: {len(active_triggers)} (Prefix: {len(triggers_prefix)})")

        for tx in txs:
            # Normalize
            if tx.id not in normalized_merchants:
                normalized_merchants[tx.id] = self.normalizer.normalize(tx.merchant)
            
            nm = normalized_merchants[tx.id]
            print(f"[DEBUG] Checking TX: {tx.merchant} -> Normalized: '{nm}'")
            
            # Match EXACT
            
            # Match EXACT
            if nm in triggers_exact:
                for t in triggers_exact[nm]:
                    candidates.append((t.offer, "MERCHANT_MATCH", tx))
                    
            # Match PREFIX
            for t in triggers_prefix:
                if nm.startswith(t.pattern_text.upper()):
                    candidates.append((t.offer, "MERCHANT_MATCH", tx))
            
            # Match MCC (if available in Transaction extra_data or column)
            # Assuming 'extra_data' has 'mcc'
            # tx_mcc = tx.extra_data.get('mcc') if tx.extra_data else None
            # if tx_mcc and tx_mcc in triggers_mcc: ...
            
        return candidates

    def _check_eligibility(self, offer: AffiliateOffer, tx: Transaction) -> bool:
        """
        Hard logic checks (Amount, Currency).
        """
        if offer.min_amount > 0 and tx.amount < offer.min_amount:
            return False
        return True

    def _check_policy(self, user_id: str, offer: AffiliateOffer) -> bool:
        """
        Checks Caps, Cooldowns, Dismissals.
        Returns True if allowed.
        """
        state = self.db.get(UserOfferState, (user_id, offer.id))
        
        if not state:
            return True # Never seen
            
        # 1. Dismissal
        if state.is_dismissed:
            if state.dismissed_until and state.dismissed_until > datetime.utcnow():
                return False
            # Hard dismiss logic or expired soft dismiss
            if state.is_dismissed and not state.dismissed_until:
                return False # Hard dismissed
                
        # 2. Offer Cap (Max 3 impressions in 7 days)
        if state.impressions_7d >= offer.max_impressions_7d:
            return False
            
        # 3. Cooldown (3 days default)
        if state.last_seen_at:
            if state.last_seen_at > datetime.utcnow() - timedelta(hours=offer.cooldown_hours):
                return False
                
        return True

    def _calculate_score(self, offer: AffiliateOffer, tx: Transaction) -> float:
        """
        Calculates relevance score.
        """
        base_score = float(offer.priority)
        
        # Context Boost: High Amount
        # If transaction is > 1.5x min_amount, boost
        if offer.min_amount > 0 and tx.amount > (offer.min_amount * 1.5):
            base_score += 20.0
            
        return base_score
