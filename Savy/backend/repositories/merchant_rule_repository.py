"""
Merchant Rule repository for AI learning from user corrections.
"""
from typing import Optional
from sqlalchemy.orm import Session
from models.transaction import MerchantRule
from .base_repository import BaseRepository


class MerchantRuleRepository(BaseRepository[MerchantRule]):
    """Repository for MerchantRule operations."""
    
    def __init__(self, db: Session):
        super().__init__(MerchantRule, db)
    
    def find_rule(self, user_id: str, merchant: str) -> Optional[MerchantRule]:
        """
        Find a merchant rule for a user.
        Searches for exact match (case-insensitive).
        """
        merchant_lower = merchant.lower().strip()
        return self.db.query(MerchantRule).filter(
            MerchantRule.user_id == user_id,
            MerchantRule.merchant_pattern == merchant_lower
        ).first()
    
    def save_rule(self, user_id: str, merchant: str, category_id: str) -> MerchantRule:
        """
        Save or update a merchant rule.
        If rule exists, update the category. Otherwise create new.
        """
        merchant_lower = merchant.lower().strip()
        
        existing = self.find_rule(user_id, merchant)
        
        if existing:
            existing.category_id = category_id
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        return self.create({
            "user_id": user_id,
            "merchant_pattern": merchant_lower,
            "category_id": category_id
        })
    
    def get_user_rules(self, user_id: str) -> list[MerchantRule]:
        """Get all rules for a user."""
        return self.db.query(MerchantRule).filter(
            MerchantRule.user_id == user_id
        ).all()

