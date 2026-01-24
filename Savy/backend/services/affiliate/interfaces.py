from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class AffiliateVertical(str, Enum):
    SHOPPING = "SHOPPING"
    TRAVEL = "TRAVEL"
    UTILITIES = "UTILITIES"
    FUEL_MOBILITY = "FUEL_MOBILITY"
    TELCO = "TELCO"
    GROCERY = "GROCERY"

class AffiliateContext(BaseModel):
    user_id: str
    locale: str = "it_IT"
    transaction_amount: Optional[float] = None
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    keywords: List[str] = []

class ScoredOffer(BaseModel):
    provider: str
    offer_id: str
    title: str
    description: str
    price: Optional[float] = None
    discount: Optional[str] = None # "-15%", "Cashback 5%"
    currency: str = "EUR"
    final_url: str # The destination URL (not the tracking one yet)
    tracking_token: Optional[str] = None # Will be populated by aggregator
    score: float = 0.0
    image_url: Optional[str] = None
    vertical: AffiliateVertical
    cta_label: str = "Vedi offerta"
    provider_metadata: Dict[str, Any] = {}

class AffiliateProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'AMAZON', 'AWIN', 'SWITCHO')"""
        pass

    @property
    @abstractmethod
    def verticals(self) -> List[AffiliateVertical]:
        """List of supported verticals"""
        pass

    @abstractmethod
    async def search_offers(
        self, 
        query: str, 
        vertical: AffiliateVertical, 
        context: AffiliateContext,
        limit: int = 3
    ) -> List[ScoredOffer]:
        """Search for offers based on query or transaction context"""
        pass

    @abstractmethod
    def build_tracking_link(self, offer: ScoredOffer, user_id: str, sub_id: str) -> str:
        """Generates the final affiliate link with SubID embedded"""
        pass
