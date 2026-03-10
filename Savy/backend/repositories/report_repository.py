"""
Repository for spending reports.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, date as date_type
from typing import List, Dict, Any, Optional
import structlog

from models.transaction import Transaction
from models.category import UserCategory

logger = structlog.get_logger()


class ReportRepository:
    """Repository for generating spending reports."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_spending_by_category(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        bank_account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get spending grouped by category for a date range.
        ONLY includes 'expense' transactions, not 'income'.
        Uses LEFT JOIN to include uncategorized transactions.
        
        Args:
            user_id: User ID
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            List of dicts with category_id, category_name, total_spent, budget_monthly
        """
        try:
            # Convert datetime to date for comparison with Transaction.transaction_date
            start = start_date.date() if isinstance(start_date, datetime) else start_date
            end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            # Query transactions grouped by category (LEFT JOIN to include uncategorized)
            base_query = (
                self.db.query(
                    Transaction.category_id,
                    UserCategory.name.label('category_name'),
                    UserCategory.icon,
                    UserCategory.color,
                    UserCategory.budget_monthly,
                    func.sum(Transaction.amount).label('total_spent'),
                    func.count(Transaction.id).label('transaction_count')
                )
                .outerjoin(UserCategory, Transaction.category_id == UserCategory.id)
            )
            
            filters = [
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                # Only include EXPENSES, not income
                or_(
                    Transaction.transaction_type == 'expense',
                    Transaction.transaction_type.is_(None)  # Legacy transactions
                )
            ]
            
            if bank_account_id:
                filters.append(Transaction.bank_account_id == bank_account_id)
                
            results = (
                base_query
                .filter(*filters)
                .group_by(
                    Transaction.category_id,
                    UserCategory.name,
                    UserCategory.icon,
                    UserCategory.color,
                    UserCategory.budget_monthly
                )
                .all()
            )
            
            # Convert to list of dicts
            report_data = []
            for row in results:
                report_data.append({
                    'category_id': row.category_id,
                    'category_name': row.category_name or 'Non categorizzate',
                    'icon': row.icon or 'help_outline',
                    'color': row.color or '#9CA3AF',  # Grey for uncategorized
                    'budget_monthly': float(row.budget_monthly) if row.budget_monthly else 0.0,
                    'total_spent': float(row.total_spent) if row.total_spent else 0.0,
                    'transaction_count': row.transaction_count
                })
            
            logger.info(
                "spending_by_category_retrieved",
                user_id=user_id,
                categories_count=len(report_data),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            return report_data
            
        except Exception as e:
            logger.error("get_spending_by_category_failed", error=str(e), user_id=user_id)
            raise
    
    def get_total_spending(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        bank_account_id: Optional[str] = None
    ) -> float:
        """
        Get total spending for a date range.
        ONLY includes 'expense' transactions, not 'income'.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Total spending amount
        """
        try:
            # Convert datetime to date for comparison with Transaction.transaction_date
            start = start_date.date() if isinstance(start_date, datetime) else start_date
            end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            filters = [
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                # Only include EXPENSES
                or_(
                    Transaction.transaction_type == 'expense',
                    Transaction.transaction_type.is_(None)  # Legacy transactions
                )
            ]
            if bank_account_id:
                filters.append(Transaction.bank_account_id == bank_account_id)
                
            result = (
                self.db.query(func.sum(Transaction.amount))
                .filter(*filters)
                .scalar()
            )
            
            total = float(result) if result else 0.0
            
            logger.info(
                "total_spending_retrieved",
                user_id=user_id,
                total=total,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            return total
            
        except Exception as e:
            logger.error("get_total_spending_failed", error=str(e), user_id=user_id)
            raise
    
    def get_total_income(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        bank_account_id: Optional[str] = None
    ) -> float:
        """
        Get total income for a date range.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Total income amount
        """
        try:
            # Convert datetime to date for comparison with Transaction.transaction_date
            start = start_date.date() if isinstance(start_date, datetime) else start_date
            end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            filters = [
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                Transaction.transaction_type == 'income'
            ]
            if bank_account_id:
                filters.append(Transaction.bank_account_id == bank_account_id)
                
            result = (
                self.db.query(func.sum(Transaction.amount))
                .filter(*filters)
                .scalar()
            )
            
            total = float(result) if result else 0.0
            
            logger.info(
                "total_income_retrieved",
                user_id=user_id,
                total=total,
                start_date=str(start),
                end_date=str(end)
            )
            
            return total
            
        except Exception as e:
            logger.error("get_total_income_failed", error=str(e), user_id=user_id)
            raise
    
    def get_category_trend(
        self,
        user_id: str,
        category_id: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "daily",
        bank_account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get spending trend for a category over time.
        
        Args:
            user_id: User ID
            category_id: Category ID
            start_date: Start date
            end_date: End date
            granularity: 'daily', 'weekly', 'monthly'
            
        Returns:
            List of {date, amount} dictionaries
        """
        try:
            start = start_date.date() if isinstance(start_date, datetime) else start_date
            end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            filters = [
                Transaction.user_id == user_id,
                Transaction.category_id == category_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                Transaction.transaction_type == 'expense'
            ]
            if bank_account_id:
                filters.append(Transaction.bank_account_id == bank_account_id)

            # Query transactions grouped by date
            results = (
                self.db.query(
                    Transaction.transaction_date,
                    func.sum(Transaction.amount).label('amount')
                )
                .filter(*filters)
                .group_by(Transaction.transaction_date)
                .order_by(Transaction.transaction_date)
                .all()
            )
            
            return [
                {
                    'date': row.transaction_date.isoformat(),
                    'amount': float(row.amount)
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error("get_category_trend_failed", error=str(e), user_id=user_id)
            raise
    
    def get_daily_cumulative_spending(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        bank_account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cumulative spending by day for the period.
        
        Args:
            user_id: User ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of {date, daily_amount, cumulative_amount}
        """
        try:
            start = start_date.date() if isinstance(start_date, datetime) else start_date
            end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            filters = [
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
                Transaction.transaction_type == 'expense'
            ]
            if bank_account_id:
                filters.append(Transaction.bank_account_id == bank_account_id)

            # Query transactions grouped by date
            results = (
                self.db.query(
                    Transaction.transaction_date,
                    func.sum(Transaction.amount).label('amount')
                )
                .filter(*filters)
                .group_by(Transaction.transaction_date)
                .order_by(Transaction.transaction_date)
                .all()
            )
            
            # Calculate cumulative
            cumulative = 0.0
            data = []
            for row in results:
                amount = float(row.amount)
                cumulative += amount
                data.append({
                    'date': row.transaction_date.isoformat(),
                    'daily_amount': amount,
                    'cumulative_amount': cumulative
                })
            
            return data
            
        except Exception as e:
            logger.error("get_daily_cumulative_spending_failed", error=str(e), user_id=user_id)
            raise
