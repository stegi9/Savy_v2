"""
Real Amazon Product Advertising API 5.0 Provider.
Uses python-amazon-paapi library for real product searches.
Falls back to mock data if API keys are not configured.
"""
from typing import List, Optional
import structlog
from config import settings
from services.affiliate.interfaces import (
    AffiliateProvider, AffiliateContext, ScoredOffer, AffiliateVertical
)

logger = structlog.get_logger()


class RealAmazonProvider(AffiliateProvider):
    """
    Amazon PA-API 5.0 provider for real product searches.
    Supports fallback to mock data when API keys are not configured.
    """
    
    def __init__(self):
        self._api = None
        self._use_mock = True
        
        # Check if real API keys are configured
        if settings.amazon_access_key and settings.amazon_secret_key:
            try:
                from amazon_paapi import AmazonApi
                self._api = AmazonApi(
                    key=settings.amazon_access_key,
                    secret=settings.amazon_secret_key,
                    tag=settings.amazon_partner_tag,
                    country=settings.amazon_country.upper(),
                    throttling=1.0  # 1 request per second (Amazon limit)
                )
                self._use_mock = False
                logger.info("amazon_paapi_initialized", country=settings.amazon_country)
            except ImportError:
                logger.warning("amazon_paapi_not_installed", 
                              message="Install with: pip install python-amazon-paapi")
            except Exception as e:
                logger.error("amazon_paapi_init_failed", error=str(e))
        else:
            logger.info("amazon_paapi_using_mock", 
                       message="No API keys configured, using mock data")
    
    @property
    def provider_name(self) -> str:
        return "AMAZON"
    
    @property
    def verticals(self) -> List[AffiliateVertical]:
        return [AffiliateVertical.SHOPPING, AffiliateVertical.GROCERY]
    
    async def search_offers(
        self,
        query: str,
        vertical: AffiliateVertical,
        context: AffiliateContext,
        limit: int = 3
    ) -> List[ScoredOffer]:
        """Search for products on Amazon."""
        
        if self._use_mock:
            return await self._mock_search(query, vertical, limit)
        
        return await self._real_search(query, vertical, limit)
    
    async def _real_search(
        self, 
        query: str, 
        vertical: AffiliateVertical, 
        limit: int
    ) -> List[ScoredOffer]:
        """Search using real Amazon PA-API."""
        try:
            # Search for products
            results = self._api.search_items(
                keywords=query,
                search_index="All",
                item_count=limit,
                resources=[
                    "Images.Primary.Large",
                    "ItemInfo.Title",
                    "ItemInfo.Features",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis"
                ]
            )
            
            if not results or not results.items:
                logger.info("amazon_search_no_results", query=query)
                return []
            
            offers = []
            for item in results.items[:limit]:
                # Extract price info
                price = 0.0
                discount = None
                if item.offers and item.offers.listings:
                    listing = item.offers.listings[0]
                    if listing.price:
                        price = listing.price.amount
                    if listing.saving_basis:
                        original = listing.saving_basis.amount
                        if original and price:
                            discount_pct = int((1 - price/original) * 100)
                            if discount_pct > 0:
                                discount = f"-{discount_pct}%"
                
                # Extract image
                image_url = None
                if item.images and item.images.primary and item.images.primary.large:
                    image_url = item.images.primary.large.url
                
                # Extract title
                title = "Prodotto Amazon"
                if item.item_info and item.item_info.title:
                    title = item.item_info.title.display_value
                
                offers.append(ScoredOffer(
                    provider="AMAZON",
                    offer_id=item.asin,
                    title=title[:80],  # Truncate long titles
                    description=f"ASIN: {item.asin}",
                    price=price,
                    discount=discount,
                    final_url=item.detail_page_url,
                    score=0.9,
                    image_url=image_url,
                    vertical=vertical,
                    cta_label="Vedi su Amazon"
                ))
            
            logger.info("amazon_search_success", query=query, results=len(offers))
            return offers
            
        except Exception as e:
            logger.error("amazon_search_failed", query=query, error=str(e))
            # Fallback to mock on error
            return await self._mock_search(query, vertical, limit)
    
    async def _mock_search(
        self, 
        query: str, 
        vertical: AffiliateVertical, 
        limit: int
    ) -> List[ScoredOffer]:
        """Mock search for development/testing."""
        q_lower = query.lower()
        results = []
        
        # Electronics keywords
        if any(kw in q_lower for kw in ["iphone", "telefono", "smartphone", "cellulare"]):
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B0CHX1W1XY",
                title="iPhone 15 Pro - 128GB",
                description="L'ultimo iPhone con chip A17 Pro",
                price=1239.00,
                discount="-5%",
                final_url="https://amazon.it/dp/B0CHX1W1XY",
                score=0.95,
                image_url="https://m.media-amazon.com/images/I/71d7rfSl0wL._AC_SL1500_.jpg",
                vertical=vertical,
                cta_label="Vedi su Amazon"
            ))
        
        if any(kw in q_lower for kw in ["cuffie", "audio", "airpods", "beats"]):
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B08HMWZBXC",
                title="Sony WH-1000XM5 Cuffie Wireless",
                description="Le migliori cuffie con cancellazione rumore",
                price=349.00,
                discount="-18%",
                final_url="https://amazon.it/dp/B08HMWZBXC",
                score=0.95,
                image_url="https://m.media-amazon.com/images/I/51SKmu2G9FL._AC_SL1000_.jpg",
                vertical=vertical,
                cta_label="Vedi su Amazon"
            ))
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B0936B5QG9",
                title="Sennheiser HD 450BT",
                description="Ottimo rapporto qualità prezzo",
                price=129.99,
                discount="-30%",
                final_url="https://amazon.it/dp/B0936B5QG9",
                score=0.85,
                image_url="https://m.media-amazon.com/images/I/61r5h8-5-HL._AC_SL1500_.jpg",
                vertical=vertical,
                cta_label="Vedi offerta"
            ))
        
        if any(kw in q_lower for kw in ["tablet", "ipad", "samsung tab"]):
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B0BN72P4ZB",
                title="iPad 10a Gen - 64GB WiFi",
                description="Display Liquid Retina da 10.9 pollici",
                price=389.00,
                discount="-12%",
                final_url="https://amazon.it/dp/B0BN72P4ZB",
                score=0.92,
                image_url="https://m.media-amazon.com/images/I/61NGnpjoRDL._AC_SL1500_.jpg",
                vertical=vertical,
                cta_label="Vedi su Amazon"
            ))
        
        if any(kw in q_lower for kw in ["computer", "laptop", "portatile", "macbook"]):
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="B0CM5JVZCK",
                title="MacBook Air M3 2024 - 256GB",
                description="Chip M3 con GPU 8-core, 18h batteria",
                price=1199.00,
                discount="-8%",
                final_url="https://amazon.it/dp/B0CM5JVZCK",
                score=0.94,
                image_url="https://m.media-amazon.com/images/I/71f5Eu5lJSL._AC_SL1500_.jpg",
                vertical=vertical,
                cta_label="Vedi su Amazon"
            ))
        
        # Generic fallback
        if not results:
            results.append(ScoredOffer(
                provider="AMAZON",
                offer_id="AMZPRIME",
                title="Amazon Prime - 30 Giorni Gratis",
                description="Spedizioni veloci e Prime Video incluso",
                price=4.99,
                discount="GRATIS",
                final_url="https://amazon.it/prime",
                score=0.5,
                image_url="https://m.media-amazon.com/images/G/29/social_marketing/prime_logo_RGB.png",
                vertical=vertical,
                cta_label="Prova Gratis"
            ))
        
        return results[:limit]
    
    def build_tracking_link(self, offer: ScoredOffer, user_id: str, sub_id: str) -> str:
        """Build Amazon tracking link with affiliate tag."""
        separator = "&" if "?" in offer.final_url else "?"
        return f"{offer.final_url}{separator}tag={settings.amazon_partner_tag}&ascsubtag={sub_id}"
