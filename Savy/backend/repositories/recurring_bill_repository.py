"""
Recurring Bill repository for bill operations.
"""
from typing import List
from sqlalchemy.orm import Session
from models.recurring_bill import RecurringBill
from .base_repository import BaseRepository


class RecurringBillRepository(BaseRepository[RecurringBill]):
    """Repository for Recurring Bill operations."""
    
    def __init__(self, db: Session):
        super().__init__(RecurringBill, db)
    
    def get_by_user(self, user_id: str) -> List[RecurringBill]:
        """Get all recurring bills for a user."""
        return self.db.query(RecurringBill).filter(
            RecurringBill.user_id == user_id
        ).order_by(RecurringBill.due_day).all()
    
    def get_active_bills(self, user_id: str) -> List[RecurringBill]:
        """Get all active recurring bills for a user."""
        return self.db.query(RecurringBill).filter(
            RecurringBill.user_id == user_id,
            RecurringBill.is_active == True
        ).order_by(RecurringBill.due_day).all()
    
    def get_by_category(self, user_id: str, category: str) -> List[RecurringBill]:
        """Get bills by category for a user."""
        return self.db.query(RecurringBill).filter(
            RecurringBill.user_id == user_id,
            RecurringBill.category == category,
            RecurringBill.is_active == True
        ).all()

