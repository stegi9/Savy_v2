"""
Merchant Normalization Service.
Cleans and standardizes merchant names for Affiliate Matching.
"""
import re
from typing import Optional

class MerchantNormalizationService:
    # Static rules for MVP. In future, load from DB table `merchant_aliases`.
    NORMALIZATION_MAP = {
        r"AMZN.*": "AMAZON",
        r"AMAZON.*": "AMAZON",
        r"PAYPAL.*FLIXBUS": "FLIXBUS",
        r"FLIXBUS.*": "FLIXBUS",
        r"BOOKING\.COM.*": "BOOKING",
        r"UBER.*EATS": "UBEREATS",
        r"UBER.*BV": "UBER", 
        r"ITULO.*": "ITULO", # Train example
        r"TRENITALIA.*": "TRENITALIA",
        r"ENEL.*": "ENEL",
        r"SERV\.ELETTR.*": "ENEL", # Common in Italy
        r"A2A.*": "A2A",
        r"SORGENCIA.*": "SORGENIA",
        r"NEN.*": "NEN",
    }

    def normalize(self, raw_merchant: str) -> str:
        """
        Normalizes a raw merchant string.
        Returns the normalized name (UPPERCASE) or the original cleaned up.
        """
        if not raw_merchant:
            return "UNKNOWN"
            
        cleaned = raw_merchant.strip().upper()
        
        # Apply Regex Rules
        for pattern, normalized in self.NORMALIZATION_MAP.items():
            if re.match(pattern, cleaned):
                return normalized
                
        return cleaned
