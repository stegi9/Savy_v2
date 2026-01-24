from typing import List, Dict, Any
import random
from services.affiliate.interfaces import AffiliateProvider, AffiliateContext, ScoredOffer, AffiliateVertical

class AmazonProvider(AffiliateProvider):
    @property
    def provider_name(self) -> str:
        return "AMAZON"

    @property
    def verticals(self) -> List[AffiliateVertical]:
        return [AffiliateVertical.SHOPPING, AffiliateVertical.GROCERY, AffiliateVertical.FUEL_MOBILITY]

    async def search_offers(
        self, 
        query: str, 
        vertical: AffiliateVertical, 
        context: AffiliateContext,
        limit: int = 3
    ) -> List[ScoredOffer]:
        
        # MOCK LOGIC - In real app, call PA-API
        # Simulate different results based on query keywords
        q_lower = query.lower()
        results = []

        if "cuffie" in q_lower or "audio" in q_lower:
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B08HMWZBXC",
                title="Sony WH-1000XM5 Cuffie Wireless",
                description="Le migliori cuffie con cancellazione rumore.",
                price=349.00,
                discount="-18%",
                final_url="https://amazon.it/dp/B08HMWZBXC",
                score=0.95,
                image_url="https://m.media-amazon.com/images/I/51SKmu2G9FL._AC_SL1000_.jpg",
                vertical=AffiliateVertical.SHOPPING,
                cta_label="Vedi su Amazon"
            ))
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B0936B5QG9",
                title="Sennheiser HD 450BT",
                description="Ottimo rapporto qualità prezzo.",
                price=129.99,
                discount="-30%",
                final_url="https://amazon.it/dp/B0936B5QG9",
                score=0.85,
                image_url="https://m.media-amazon.com/images/I/61r5h8-5-HL._AC_SL1500_.jpg",
                vertical=AffiliateVertical.SHOPPING,
                cta_label="Vedi offerta"
            ))
        elif "spesa" in q_lower or "cibo" in q_lower:
             results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="AMZFRESH01",
                title="Amazon Fresh - Sconto 10€",
                description="Sulla tua prima spesa di almeno 50€.",
                price=0.0,
                discount="10€ Coupon",
                final_url="https://amazon.it/fresh",
                score=0.99,
                image_url="https://m.media-amazon.com/images/G/29/marketing/prime/fresh/box_mockup.png",
                vertical=AffiliateVertical.GROCERY,
                cta_label="Riscatta Coupon"
            ))
        else:
             # Generic Fallback
             results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="AMZPRIME",
                title="Amazon Prime - 30 Giorni Gratis",
                description="Spedizioni veloci e Prime Video incluso",
                price=4.99,
                discount="GRATIS",
                final_url="https://amazon.it/prime",
                score=0.5, # Low score if generic
                image_url="https://m.media-amazon.com/images/G/29/social_marketing/prime_logo_RGB.png",
                vertical=AffiliateVertical.SHOPPING,
                cta_label="Prova Gratis"
            ))

        return results[:limit]

    def build_tracking_link(self, offer: ScoredOffer, user_id: str, sub_id: str) -> str:
        # Mock Tracking Link Construction
        # Append tag and subId
        separator = "&" if "?" in offer.final_url else "?"
        return f"{offer.final_url}{separator}tag=savy-21&ascsubtag={sub_id}"
