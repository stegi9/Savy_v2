"""
Booking.com Affiliate API Provider.
Provides hotel search functionality for the travel vertical.
Falls back to mock data if API keys are not configured.
"""
from typing import List
import structlog
import httpx
from config import settings
from services.affiliate.interfaces import (
    AffiliateProvider, AffiliateContext, ScoredOffer, AffiliateVertical
)

logger = structlog.get_logger()


class BookingProvider(AffiliateProvider):
    """
    Booking.com affiliate provider for hotel searches.
    Uses Demand API when configured, mock data otherwise.
    """
    
    BASE_URL = "https://distribution-xml.booking.com/2.0/json"
    
    def __init__(self):
        self._use_mock = True
        self._client = None
        
        if settings.booking_affiliate_id and settings.booking_api_key:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                auth=(settings.booking_affiliate_id, settings.booking_api_key),
                timeout=10.0
            )
            self._use_mock = False
            logger.info("booking_api_initialized")
        else:
            logger.info("booking_api_using_mock")
    
    @property
    def provider_name(self) -> str:
        return "BOOKING"
    
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
        """Search for hotels on Booking.com."""
        
        if self._use_mock:
            return await self._mock_search(query, limit)
        
        return await self._real_search(query, limit)
    
    async def _real_search(self, query: str, limit: int) -> List[ScoredOffer]:
        """Search using real Booking.com API."""
        try:
            # Get city ID first
            city_response = await self._client.get(
                "/cities",
                params={"city_names": query, "languages": "it"}
            )
            cities = city_response.json().get("result", [])
            
            if not cities:
                return await self._mock_search(query, limit)
            
            city_id = cities[0].get("city_id")
            
            # Search hotels
            hotels_response = await self._client.get(
                "/hotels",
                params={
                    "city_ids": city_id,
                    "rows": limit,
                    "languages": "it"
                }
            )
            hotels = hotels_response.json().get("result", [])
            
            offers = []
            for hotel in hotels[:limit]:
                offers.append(ScoredOffer(
                    provider="BOOKING",
                    offer_id=str(hotel.get("hotel_id")),
                    title=hotel.get("name", "Hotel"),
                    description=f"{hotel.get('star_rating', 3)}⭐ - {hotel.get('address', '')}",
                    price=float(hotel.get("min_rate", 0)),
                    discount=None,
                    final_url=hotel.get("url", f"https://booking.com/hotel/{hotel.get('hotel_id')}"),
                    score=float(hotel.get("review_score", 8)) / 10,
                    image_url=hotel.get("photo_url"),
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                ))
            
            return offers
            
        except Exception as e:
            logger.error("booking_search_failed", error=str(e))
            return await self._mock_search(query, limit)
    
    async def _mock_search(self, query: str, limit: int) -> List[ScoredOffer]:
        """Mock search for development/testing."""
        q_lower = query.lower()
        results = []
        
        # Rome hotels
        if "roma" in q_lower or "rome" in q_lower:
            results = [
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_ROME_001",
                    title="Hotel Artemide ★★★★",
                    description="Via Nazionale 22 - Vicino Stazione Termini",
                    price=145.00,
                    discount="-15%",
                    final_url="https://booking.com/hotel/it/artemide.html",
                    score=0.92,
                    image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/275162028.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                ),
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_ROME_002",
                    title="The Roman Empire Luxury Suite",
                    description="Centro Storico - Vista Colosseo",
                    price=220.00,
                    discount="-10%",
                    final_url="https://booking.com/hotel/it/roman-empire.html",
                    score=0.95,
                    image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/412389112.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                )
            ]
        
        # Milan hotels
        elif "milano" in q_lower or "milan" in q_lower:
            results = [
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_MILAN_001",
                    title="NH Milano Touring ★★★★",
                    description="Via Tarchetti 2 - Centro Milano",
                    price=135.00,
                    discount="-20%",
                    final_url="https://booking.com/hotel/it/nhtouringmilano.html",
                    score=0.88,
                    image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/270050836.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                ),
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_MILAN_002",
                    title="Starhotels Rosa Grand ★★★★",
                    description="Piazza Fontana 3 - Vicino Duomo",
                    price=189.00,
                    discount="-12%",
                    final_url="https://booking.com/hotel/it/starhotelsrosagrand.html",
                    score=0.91,
                    image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/481662234.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                )
            ]
        
        # Beach/Sea vacation
        elif any(kw in q_lower for kw in ["mare", "spiaggia", "beach", "costa"]):
            results = [
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_BEACH_001",
                    title="Grand Hotel Rimini ★★★★★",
                    description="Lungomare Rimini - Accesso privato spiaggia",
                    price=210.00,
                    discount="-25%",
                    final_url="https://booking.com/hotel/it/grandrimini.html",
                    score=0.94,
                    image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/441234567.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                ),
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_BEACH_002",
                    title="Villaggio Turistico Sardegna",
                    description="Costa Smeralda - All Inclusive",
                    price=175.00,
                    discount="-18%",
                    final_url="https://booking.com/hotel/it/villaggio-sardegna.html",
                    score=0.89,
                    image_url="https://cf.bstatic.com/xdata/images/hotel/max1024x768/398765432.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Prenota ora"
                )
            ]
        
        # Generic travel fallback
        else:
            results = [
                ScoredOffer(
                    provider="BOOKING",
                    offer_id="BOOKING_PROMO",
                    title="Offerte Last Minute Italia",
                    description="Fino al 40% di sconto su hotel selezionati",
                    price=89.00,
                    discount="-40%",
                    final_url="https://booking.com/deals.html",
                    score=0.7,
                    image_url="https://cf.bstatic.com/xdata/images/xphoto/540x405/146670858.jpg",
                    vertical=AffiliateVertical.TRAVEL,
                    cta_label="Vedi offerte"
                )
            ]
        
        return results[:limit]
    
    def build_tracking_link(self, offer: ScoredOffer, user_id: str, sub_id: str) -> str:
        """Build Booking.com tracking link with affiliate ID."""
        separator = "&" if "?" in offer.final_url else "?"
        aid = settings.booking_affiliate_id or "2397407"  # Default affiliate ID
        return f"{offer.final_url}{separator}aid={aid}&label=savy_{sub_id}"
