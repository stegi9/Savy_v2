"""
Affiliate API Controller.
Exposes endpoints for Recommendations, Interactions, and Redirects.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
import structlog
from typing import List, Optional
from datetime import datetime

from db.database import get_db
from api.routes.auth_controller import get_current_user
from models.user import User
from models.affiliate import (
    UserRecommendation, 
    AffiliateInteraction, 
    PlacementType, 
    InteractionType,
    AffiliateOffer,
    AffiliatePartner
)
from services.affiliate_redirect_service import AffiliateRedirectService
from services.affiliate_matching_service import AffiliateMatchingService
from schemas import StandardResponse
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter(prefix="/affiliate", tags=["Affiliate Advisor"])

# Schemas
class RecommendationRequest(BaseModel):
    placement: str = "DASHBOARD"
    max_items: int = 1

class InteractionRequest(BaseModel):
    public_id: str
    event: str # IMPRESSION, DISMISS, CLICK
    placement: Optional[str] = None
    idempotency_key: Optional[str] = None
    metadata: Optional[dict] = None

class RecommendationItem(BaseModel):
    public_id: str
    title: str
    body: Optional[str]
    action_token: str
    score: float
    image_url: Optional[str]
    badge: Optional[str] = None

class RecommendationResponse(BaseModel):
    placement: str
    ab_variant: str = "CONTROL"
    items: List[RecommendationItem]

# Endpoints

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    req: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get contextual recommendations for the user.
    Uses pre-calculated results from `user_recommendations` table.
    """
    try:
        # 1. Matching Service (Lazy Load / Verification)
        # In a real heavy system, this is async worker only.
        # For MVP, we might want to trigger a quick check if no recs exist?
        # No, respect architecture: Worker populates, API reads.
        
        # 2. Fetch Active Recommendations
        stmt = (
            select(UserRecommendation, AffiliateOffer)
            .join(AffiliateOffer, UserRecommendation.offer_id == AffiliateOffer.id)
            .where(
                UserRecommendation.user_id == current_user.id,
                UserRecommendation.placement == req.placement,
                UserRecommendation.expires_at > datetime.utcnow()
            )
            .order_by(desc(UserRecommendation.score))
            .limit(req.max_items)
        )
        
        results = db.execute(stmt).all()
        
        items = []
        for rec, offer in results:
            # Re-generate a fresh token if needed? 
            # The spec says token is generated at persistence time. We use that one.
            # We assume token_hash is in DB, but we need the RAW token to send to client.
            # WAIT: We stored `token_hash` in DB. We CANNOT recover raw token.
            # ISSUE: If we pre-calculate in worker, how do we send the raw token to client later?
            # 
            # FIX from Spec step 3: "Invia raw_token al client nel payload JSON" -> implies immediate return or storage.
            # If we store only HASH, we can't show it later.
            # 
            # ARCHITECTURE FIX:
            # Option A: Store raw_token encrypted (User-retrievable).
            # Option B: Generate new ephemeral token on READ (API).
            # 
            # Let's go with B (Secure & Fresh).
            # The Worker found the Match. The API generates the specific Click Token for this session.
            
            redirect_service = AffiliateRedirectService(db)
            raw_token, public_id = redirect_service.generate_token(
                user_id=current_user.id,
                offer_id=offer.id,
                placement=req.placement,
                score=rec.score,
                reason_code=rec.reason_code
            )
            
            items.append(RecommendationItem(
                public_id=public_id,
                title=offer.title,
                body=offer.copy_text,
                action_token=raw_token,
                score=rec.score,
                image_url=offer.image_url,
                badge="Partner" # or logic based on priority
            ))
            
        return RecommendationResponse(
            placement=req.placement,
            ab_variant="CONTROL", # Placeholder for A/B logic
            items=items
        )

    except Exception as e:
        logger.error("affiliate_recommendations_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/interactions", status_code=202)
async def track_interaction(
    req: InteractionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log interactions (Impression, Dismiss).
    """
    try:
        # Idempotency Check (if key provided)
        if req.idempotency_key:
            exists = db.query(AffiliateInteraction).filter_by(
                user_id=current_user.id,
                idempotency_key=req.idempotency_key
            ).first()
            if exists:
                return {"status": "ignored_idempotent"}

        # Log
        interaction = AffiliateInteraction(
            user_id=current_user.id,
            event_type=req.event, # ENUM mapping might be needed if strictly typed in Schema
            placement=req.placement,
            idempotency_key=req.idempotency_key,
            offer_id=0, # Need to lookup from public_id...
            recommendation_id=0
        )
        
        # We need to link public_id back to recommendation/offer
        # If rec is ephemeral, we might rely on the token/public_id being in `user_recommendations`
        # But `generate_token` creates a NEW `user_recommendation` entry.
        # So `req.public_id` SHOULD exist in `user_recommendations`.
        
        rec = db.query(UserRecommendation).filter_by(public_id=req.public_id).first()
        if rec:
            interaction.recommendation_id = rec.id
            interaction.offer_id = rec.offer_id
            
            # Update Denormalized State if DISMISS
            if req.event == "DISMISS":
               from models.affiliate import UserOfferState
               state = db.get(UserOfferState, (current_user.id, rec.offer_id))
               if not state:
                   state = UserOfferState(user_id=current_user.id, offer_id=rec.offer_id)
                   db.add(state)
               
               state.is_dismissed = True
               state.dismissed_until = datetime.utcnow() + getattr(datetime, 'timedelta')(days=90) # Hard dismiss default
               
            db.add(interaction)
            db.commit()
        else:
            logger.warning("interaction_rec_not_found", public_id=req.public_id)

        return {"status": "accepted"}

    except Exception as e:
        logger.error("affiliate_interaction_failed", error=str(e))
        # Don't block client
        return {"status": "error", "detail": str(e)}


@router.get("/redirect/{token}")
async def redirect_offer(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Secure Redirect Endpoint.
    """
    service = AffiliateRedirectService(db)
    target_url = service.resolve_token(
        raw_token=token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    if not target_url:
        # 410 or custom error page
        raise HTTPException(status_code=410, detail="Offerta non più disponibile o scaduta.")
        
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=target_url, status_code=302)
