from typing import List, Dict, Any
from services.affiliate.interfaces import AffiliateProvider, AffiliateContext, ScoredOffer, AffiliateVertical

class TravelProvider(AffiliateProvider):
    @property
    def provider_name(self) -> str:
        return "TRAVEL_GENERIC" # Could represent Booking.com or Skyscanner

    @property
    def verticals(self) -> List[AffiliateVertical]:
        return [AffiliateVertical.TRAVEL]

    async def search_offers(
        self, 
        query: str, 
        vertical: AffiliateVertical, 
        context: AffiliateContext,
        limit: int = 3
    ) -> List[ScoredOffer]:
        
        q_lower = query.lower()
        results = []

        if "roma" in q_lower:
             results.append(ScoredOffer(
                provider="BOOKING",
                offer_id="HTL_ROMA_01",
                title="Hotel Colosseo View",
                description="4 Stelle, colazione inclusa. Cancellazione gratuita.",
                price=120.00,
                discount="-20%",
                final_url="https://booking.com/hotel/it/colosseo-view",
                score=0.92,
                image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/12345678.jpg",
                vertical=AffiliateVertical.TRAVEL,
                cta_label="Vedi disponibilità"
            ))
        
        if "milano" in q_lower:
             results.append(ScoredOffer(
                provider="SKYSCANNER",
                offer_id="FLT_MIL_01",
                title="Volo Low Cost per Milano",
                description="Andata e ritorno da 45€",
                price=45.00,
                discount="Best Price",
                final_url="https://skyscanner.it/flights",
                score=0.88,
                image_url="https://content.skyscnr.com/m/1652427a05214800/original/eyeem-106524883.jpg",
                vertical=AffiliateVertical.TRAVEL,
                cta_label="Cerca voli"
            ))
            
        return results

    def build_tracking_link(self, offer: ScoredOffer, user_id: str, sub_id: str) -> str:
        return f"{offer.final_url}?aid=394852&label={sub_id}"
