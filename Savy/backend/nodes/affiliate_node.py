import structlog
from typing import Dict, Any, List
from services.affiliate.aggregator import AffiliateAggregatorService
from services.affiliate.interfaces import AffiliateVertical, AffiliateContext, ScoredOffer
from services.affiliate.providers.real_amazon_provider import RealAmazonProvider
from services.affiliate.providers.booking_provider import BookingProvider
from services.intent_detector import detect_intent_and_entities, map_vertical_to_enum
from db.database import SessionLocal
from config import settings

logger = structlog.get_logger()

class AffiliateNode:
    """
    LangGraph node that proactively checks for affiliate offers based on user input.
    Uses LLM-powered intent detection for smart offer matching.
    """
    def __init__(self):
        pass

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input state keys: 'user_query', 'user_id'
        Output update: 'affiliate_offers' (List[Dict])
        """
        user_query = state.get("user_query", "")
        user_id = state.get("user_id")
        
        if not user_query or not user_id:
            return {"affiliate_offers": []}

        logger.info("affiliate_node_start", query=user_query)

        # 1. Use LLM to detect intent (smart, no keywords needed)
        intent = await detect_intent_and_entities(user_query)
        
        # If no purchase intent detected, skip affiliate search
        if not intent.get("has_purchase_intent", False):
            logger.info("no_purchase_intent_detected", query=user_query)
            return {"affiliate_offers": []}
        
        # 2. Get the vertical and search query from LLM analysis
        vertical = map_vertical_to_enum(intent.get("vertical", ""))
        search_query = intent.get("product_query", user_query)
        
        if not vertical:
            # Default to shopping for generic purchase intent
            vertical = AffiliateVertical.SHOPPING
            
        logger.info("intent_detected", 
                    vertical=vertical.value if vertical else None, 
                    search_query=search_query,
                    entities=intent.get("entities", []))

        # 3. Run Aggregator with REAL providers
        offers = []
        with SessionLocal() as db:
            aggr = AffiliateAggregatorService(db)
            aggr.register_provider(RealAmazonProvider())
            aggr.register_provider(BookingProvider())

            context = AffiliateContext(
                user_id=str(user_id),
                keywords=intent.get("entities", []) or search_query.split()
            )

            offers = await aggr.search_offers(
                vertical=vertical,
                query=search_query,
                context=context,
                limit=3
            )

        # 4. Serialize for Chat Output
        offers_data = []
        for offer in offers:
            offers_data.append({
                "type": "affiliate_card",
                "title": offer.title,
                "subtitle": offer.description,
                "badge": offer.discount,
                "price": f"€{offer.price:.2f}" if offer.price else None,
                "image_url": offer.image_url,
                "cta_label": offer.cta_label,
                "redirect_url": f"/affiliate/r/{offer.tracking_token}",
                "provider": offer.provider
            })

        logger.info("affiliate_node_complete", count=len(offers_data))
        return {"affiliate_offers": offers_data}

