import asyncio
from typing import List, Dict, Optional
import structlog
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from services.affiliate.interfaces import AffiliateProvider, AffiliateContext, ScoredOffer, AffiliateVertical
from models.tracking import AffiliateClickToken

logger = structlog.get_logger()

class AffiliateAggregatorService:
    def __init__(self, db: Session):
        self.db = db
        self.providers: Dict[str, AffiliateProvider] = {}
        # Simple in-memory cache for MVP: Key -> (timestamp, List[ScoredOffer])
        self._cache: Dict[str, tuple] = {} 

    def register_provider(self, provider: AffiliateProvider):
        """Registers a provider plugin"""
        logger.info(f"Registering provider: {provider.provider_name} for verticals: {provider.verticals}")
        self.providers[provider.provider_name] = provider

    async def search_offers(
        self, 
        vertical: AffiliateVertical, 
        query: str, 
        context: AffiliateContext,
        limit: int = 3
    ) -> List[ScoredOffer]:
        """
        Aggregates offers from all relevant providers.
        """
        # 1. Check Cache
        cache_key = f"{context.user_id}:{vertical}:{query.lower().strip()}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("affiliate_cache_hit", key=cache_key)
            return cached

        # 2. Select Providers
        active_providers = [
            p for p in self.providers.values() 
            if vertical in p.verticals
        ]
        
        if not active_providers:
            logger.warning("no_providers_for_vertical", vertical=vertical)
            return []

        # 3. Parallel Query
        tasks = []
        for p in active_providers:
            tasks.append(p.search_offers(query, vertical, context, limit=5))
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_offers: List[ScoredOffer] = []
        for i, res in enumerate(results_list):
            if isinstance(res, Exception):
                logger.error("provider_error", provider=active_providers[i].provider_name, error=str(res))
            elif isinstance(res, list):
                all_offers.extend(res)

        # 4. Filter & Score & Deduplicate
        # Simple Logic: Sort by Score Descending
        all_offers.sort(key=lambda x: x.score, reverse=True)
        
        # Take Top N
        final_offers = all_offers[:limit]

        # 5. Generate Tracking Tokens (Persist to DB)
        for offer in final_offers:
            token = self._generate_click_token(offer, context.user_id)
            offer.tracking_token = token
            # Update final_url to point to our redirector (UI uses this)
            # Actually models/interfaces defines final_url as DESTINATION
            # We construct the redirect URL in the UI using tracking_token
            # But wait, User asked for "redirect_url = /r/{token}" in the smart card.
            # So let's override final_url or rely on frontend to build it? 
            # Better: Keep final_url as 'real' URL for debug, but UI logic uses /r/{token}
            pass

        # 6. Cache Result
        self._set_cache(cache_key, final_offers)

        return final_offers

    def _generate_click_token(self, offer: ScoredOffer, user_id: str) -> str:
        """Creates a persisten token in DB"""
        token = secrets.token_urlsafe(32)
        
        db_token = AffiliateClickToken(
            token=token,
            provider=offer.provider,
            offer_id=offer.offer_id,
            vertical=offer.vertical.value,
            user_id_hash=user_id, # In MVP we store direct user_id, hash later for privacy
            payload_min={
                "landing_url": offer.final_url,
                "title": offer.title
            },
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        self.db.add(db_token)
        self.db.commit()
        return token

    def _get_from_cache(self, key: str) -> Optional[List[ScoredOffer]]:
        if key in self._cache:
            ts, data = self._cache[key]
            if datetime.utcnow() - ts < timedelta(minutes=10):
                return data
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: List[ScoredOffer]):
        self._cache[key] = (datetime.utcnow(), data)
