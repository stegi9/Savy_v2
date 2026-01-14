"""
User repository for profile operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User/Profile operations."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return super().get_by_id(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create_demo_user(self) -> User:
        """Create or get demo user."""
        demo_uuid = "00000000-0000-0000-0000-000000000001"
        existing = self.get_by_id(demo_uuid)
        
        if existing:
            return existing
        
        from utils.security import hash_password
        
        return self.create({
            "id": demo_uuid,
            "email": "stegi@gmail.com",
            "hashed_password": hash_password("ciaociao1234"),
            "full_name": "Demo User",
            "current_balance": 1500.00,
            "currency": "EUR"
        })
    
    def update_balance(self, user_id: str, new_balance: float) -> Optional[User]:
        """Update user's current balance."""
        return self.update(user_id, {"current_balance": new_balance})
    
    def update_settings(self, user_id: str, settings: dict) -> Optional[User]:
        """Update user settings."""
        # Filter out None values
        update_data = {k: v for k, v in settings.items() if v is not None}
        if not update_data:
            return self.get_by_id(user_id)
        return self.update(user_id, update_data)
    
    def get_settings(self, user_id: str) -> Optional[dict]:
        """Get user settings."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # Convert Decimal to float properly
        balance = user.current_balance
        if balance is not None:
            balance = float(balance)
        else:
            balance = 0.0
            
        budget = user.monthly_budget
        if budget is not None:
            budget = float(budget)
        else:
            budget = 2000.0
            
        return {
            "full_name": user.full_name,
            "current_balance": balance,
            "monthly_budget": budget,
            "currency": user.currency or "EUR",
            "budget_notifications": user.budget_notifications if user.budget_notifications is not None else True,
            "ai_tips_enabled": user.ai_tips_enabled if user.ai_tips_enabled is not None else True,
            "optimization_alerts": user.optimization_alerts if user.optimization_alerts is not None else True,
        }