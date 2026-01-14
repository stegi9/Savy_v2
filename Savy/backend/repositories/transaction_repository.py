"""
Transaction repository for transaction operations.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.transaction import Transaction
from .base_repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction operations."""
    
    def __init__(self, db: Session):
        super().__init__(Transaction, db)
    
    def get_user_transactions(
        self, 
        user_id: str, 
        limit: int = 50, 
        needs_review: Optional[bool] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Transaction]:
        """Get user transactions ordered by date (most recent first)."""
        query = self.db.query(Transaction)\
            .filter(Transaction.user_id == user_id)
        
        if needs_review is not None:
            query = query.filter(Transaction.needs_review == needs_review)
            
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
            
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        return query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())\
            .limit(limit)\
            .all()
    
    def get_transactions_by_date_range(self, user_id: str, start_date: date, end_date: date) -> List[Transaction]:
        """Get transactions within a date range."""
        return self.db.query(Transaction)\
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )\
            .order_by(Transaction.transaction_date.desc())\
            .all()
    
    def get_spending_by_category(self, user_id: str, start_date: date, end_date: date) -> List[dict]:
        """Get spending grouped by category for a date range."""
        results = self.db.query(
            Transaction.category,
            Transaction.subcategory,
            func.sum(Transaction.amount).label('total_spent')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).group_by(Transaction.category, Transaction.subcategory).all()
        
        return [
            {
                "category": row.category,
                "subcategory": row.subcategory,
                "total_spent": float(row.total_spent)
            }
            for row in results
        ]
    
    def create_transaction(
        self,
        user_id: str,
        merchant: str,
        amount: float,
        date: date,
        transaction_type: str = "expense",
        category_id: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        needs_review: bool = False
    ) -> Transaction:
        """Create a new transaction with AI categorization support."""
        transaction = Transaction(
            user_id=user_id,
            merchant=merchant,
            amount=amount,
            transaction_type=transaction_type,
            transaction_date=date,
            category_id=category_id,
            category=category,
            description=description,
            ai_confidence=ai_confidence,
            needs_review=needs_review
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction

    def update_transaction_category(
        self,
        transaction_id: str,
        category_id: str
    ) -> Transaction:
        """Update transaction category (manual override)."""
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        transaction.category_id = category_id
        transaction.needs_review = False  # Mark as reviewed
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_transactions_needing_review(self, user_id: str) -> List[Transaction]:
        """Get transactions that need manual review."""
        return self.db.query(Transaction)\
            .filter(
                Transaction.user_id == user_id,
                Transaction.needs_review == True
            )\
            .order_by(Transaction.transaction_date.desc())\
            .all()


