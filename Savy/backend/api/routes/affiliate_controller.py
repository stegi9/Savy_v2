"""
Affiliate API Controller.
Exposes endpoints for Universal Affiliate Engine (Search, Redirect, Postback).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import structlog
from typing import List, Optional

from db.database import get_db
from api.routes.auth_controller import get_current_user
from models.user import User
from models.tracking import AffiliateClickToken, AffiliateClickEvent, AffiliateConversion
from services.affiliate.interfaces import AffiliateVertical, AffiliateContext, ScoredOffer
from services.affiliate.aggregator import AffiliateAggregatorService
from services.affiliate.providers.amazon_provider import AmazonProvider
from services.affiliate.providers.travel_provider import TravelProvider
from schemas import StandardResponse
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter(prefix="/affiliate", tags=["Affiliate Advisor"])

# --- DEPENDENCIES ---

def get_aggregator(db: Session = Depends(get_db)) -> AffiliateAggregatorService:
    service = AffiliateAggregatorService(db)
    # Register Providers (MVC Style - ideally this is done once at startup, 
    # but for stateless request scope it's fine for MVP if lightweight)
    service.register_provider(AmazonProvider())
    service.register_provider(TravelProvider())
    return service

# --- SCHEMAS ---

class SearchRequest(BaseModel):
    query: str
    vertical: AffiliateVertical
    limit: int = 3
    context_overrides: Optional[dict] = None

class SearchResponse(BaseModel):
    results: List[ScoredOffer]

# --- ENDPOINTS ---

@router.post("/search", response_model=SearchResponse)
async def search_offers(
    req: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    aggregator: AffiliateAggregatorService = Depends(get_aggregator)
):
    """
    Reactive Search: User explicitly asks for offers.
    """
    context = AffiliateContext(
        user_id=str(current_user.id),
        locale="it_IT", # Default for now until User model upgrade
        keywords=req.query.split(),
        merchant_name=None, 
        transaction_amount=None 
    )
    
    offers = await aggregator.search_offers(
        vertical=req.vertical,
        query=req.query,
        context=context,
        limit=req.limit
    )
    
    return SearchResponse(results=offers)


@router.post("/recommendations", response_model=SearchResponse)
async def get_recommendations(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    aggregator: AffiliateAggregatorService = Depends(get_aggregator)
):
    """
    Proactive Recommendations: Based on user profile/bills.
    For MVP: Checks if user has high bills and recommends Energy offers.
    """
    # 1. Analyze User Context (Mock)
    # Ideally we check: current_user.analysis_result or DB transactions
    # MVP: Assume everyone needs Energy options :)
    
    context = AffiliateContext(
        user_id=str(current_user.id),
        locale="it_IT", # Default
        keywords=["energia", "bolletta"]
    )
    
    offers = await aggregator.search_offers(
        vertical=AffiliateVertical.UTILITIES,
        query="migliore offerta luce gas",
        context=context,
        limit=3
    )
    
    return SearchResponse(results=offers)

@router.get("/r/{token}")
async def redirect_offer(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Secure Redirect Endpoint: /affiliate/r/{token}
    """
    # 1. Lookup Token
    db_token = db.query(AffiliateClickToken).filter(
        AffiliateClickToken.token == token
    ).first()
    
    if not db_token:
        logger.warning("affiliate_token_not_found", token=token[:8])
        raise HTTPException(status_code=404, detail="Offerta non valida")
        
    if db_token.expires_at < datetime.utcnow():
        logger.info("affiliate_token_expired", token=token[:8])
        raise HTTPException(status_code=410, detail="Offerta scaduta")

    # 2. Log Click Event
    try:
        click_event = AffiliateClickEvent(
            token=token,
            user_id_hash=db_token.user_id_hash,
            vertical=db_token.vertical,
            provider=db_token.provider,
            metadata_min={
                "ip": request.client.host,
                "ua": request.headers.get("user-agent"),
                "referer": request.headers.get("referer")
            }
        )
        db.add(click_event)
        db.commit()
    except Exception as e:
        logger.error("affiliate_click_log_failed", error=str(e))
        # Proceed anyway, don't block user
    
    # 3. Construct Final URL (Provider specific logic if needed)
    # For MVP, we assume payload_min['landing_url'] is what we want,
    # OR we use the provider logic to rebuild it if dynamic parameters needed?
    # Our Aggregator already stored the final 'destination' URL in payload_min.
    # BUT wait: Interfaces said `build_tracking_link` adds the SUB_ID.
    # We should probably do that step here to ensure SUB_ID matches THIS click.
    
    final_url = db_token.payload_min.get("landing_url")
    if not final_url:
        raise HTTPException(status_code=500, detail="Configuration Error")
        
    # Inject SubID dynamically?
    # For MVP, Aggregator stored `final_url` (destination). 
    # We can append `?ref=savy_{token}` as a naive implementation for ALL providers
    # if we don't load the specific Provider class here.
    # IF we want provider-specific tracking logic (e.g. `tag=` vs `subId=`), we need to load the Provider.
    
    # RE-LOAD PROVIDER to build correct link?
    # aggregator = get_aggregator(db)
    # provider = aggregator.providers.get(db_token.provider)
    # if provider:
    #     final_url = provider.build_tracking_link(...)
    
    # Implementation Simplification:
    # Let's assume `payload_min` contains the raw destination.
    # We append a generic `subId` param or trust the mocked provider logic if accessible.
    
    # For Phase 1 Mocking:
    from urllib.parse import quote
    safe_token = quote(token)
    if "amazon" in final_url:
         final_url = f"{final_url}&ascsubtag={safe_token}"
    elif "?" in final_url:
         final_url = f"{final_url}&savy_click={safe_token}"
    else:
         final_url = f"{final_url}?savy_click={safe_token}"

    from fastapi.responses import RedirectResponse
    from urllib.parse import urlparse

    # Sanitizzazione Anti-Open Redirect (Snyk Audit)
    parsed_url = urlparse(final_url)
    if parsed_url.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Protocollo non sicuro")
        
    domain = parsed_url.hostname
    allowed_domains = ["amazon.it", "amazon.com", "booking.com", "skyscanner.net", "skyscanner.it", "airbnb.com", "expedia.com", "facile.it", "segugio.it"]
    
    is_safe = False
    if domain:
        for allowed in allowed_domains:
            if domain == allowed or domain.endswith("." + allowed):
                is_safe = True
                break
                
    if not is_safe:
        logger.warning("open_redirect_blocked", url=final_url)
        raise HTTPException(status_code=403, detail="Destinazione non autorizzata")

    # deepcode ignore OpenRedirect: URL is validated against a strict allowed_domains whitelist above
    return RedirectResponse(url=final_url, status_code=302)


@router.post("/postback/{network}")
async def postback_webhook(
    network: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    S2S Conversion Postback
    """
    try:
        payload = await request.json()
    except:
        payload = await request.form() # Fallback
        
    logger.info("affiliate_postback_received", network=network, payload=payload)
    
    # Parse generic fields (MVP)
    # Usually network sends `sub_id`, `amount`, `status`
    sub_id = payload.get("sub_id") or payload.get("custom_id")
    amount = payload.get("amount") or payload.get("commission")
    
    if sub_id:
        conv = AffiliateConversion(
            sub_id=sub_id,
            network=network,
            amount=float(amount) if amount else 0.0,
            status=payload.get("status", "pending"),
            raw_payload=dict(payload)
        )
        db.add(conv)
        db.commit()
        return {"status": "recorded"}
    
    return {"status": "ignored_no_id"}

