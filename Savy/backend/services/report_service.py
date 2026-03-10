"""
Service layer for spending reports.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import structlog

from repositories.report_repository import ReportRepository
from repositories.user_repository import UserRepository

logger = structlog.get_logger()


class ReportService:
    """Business logic for spending reports."""
    
    def __init__(self, report_repository: ReportRepository, user_repository: UserRepository = None):
        self.report_repository = report_repository
        self.user_repository = user_repository
    
    def generate_spending_report(
        self,
        user_id: str,
        period: str = "monthly",
        start_date: datetime = None,
        end_date: datetime = None,
        bank_account_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate a spending report for the user.
        
        Args:
            user_id: User ID
            period: Report period ('weekly', 'monthly', 'yearly', 'custom')
            start_date: Optional start date for custom period
            end_date: Optional end date for custom period
            
        Returns:
            Dict with report data including categories, totals, and budget info
        """
        try:
            # Calculate date range based on period
            if not end_date:
                end_date = datetime.now()
            
            if period == "custom" and start_date:
                # Use provided dates
                pass
            elif period == "weekly":
                start_date = end_date - timedelta(days=7)
            elif period == "yearly":
                start_date = end_date - timedelta(days=365)
            else:  # monthly (default)
                start_date = end_date.replace(day=1)
            
            # Get spending by category (only expenses)
            categories = self.report_repository.get_spending_by_category(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                bank_account_id=bank_account_id
            )
            
            # Get total income for the period
            total_income = self.report_repository.get_total_income(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                bank_account_id=bank_account_id
            )
            
            # Calculate totals
            total_spent = sum(cat['total_spent'] for cat in categories)
            
            # Get user's global monthly budget from settings
            total_budget = 0.0
            if self.user_repository:
                user = self.user_repository.get_by_id(user_id)
                if user and user.monthly_budget:
                    total_budget = float(user.monthly_budget)
            
            # Fallback to sum of category budgets if no global budget set
            if total_budget == 0:
                total_budget = sum(cat['budget_monthly'] for cat in categories)
            
            # Calculate percentages and budget status
            for category in categories:
                if category['budget_monthly'] > 0:
                    category['budget_percentage'] = (
                        category['total_spent'] / category['budget_monthly']
                    ) * 100
                    category['remaining_budget'] = (
                        category['budget_monthly'] - category['total_spent']
                    )
                    category['is_over_budget'] = category['total_spent'] > category['budget_monthly']
                else:
                    category['budget_percentage'] = 0.0
                    category['remaining_budget'] = 0.0
                    category['is_over_budget'] = False
                
                # Calculate percentage of total spending
                if total_spent > 0:
                    category['percentage_of_total'] = (
                        category['total_spent'] / total_spent
                    ) * 100
                else:
                    category['percentage_of_total'] = 0.0
            
            # Sort by total spent (descending)
            categories.sort(key=lambda x: x['total_spent'], reverse=True)
            
            report = {
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_spent': total_spent,
                'total_income': total_income,
                'net_balance': total_income - total_spent,  # Entrate - Uscite
                'total_budget': total_budget,
                'budget_remaining': total_budget - total_spent,
                'budget_percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0.0,
                'is_over_budget': total_spent > total_budget if total_budget > 0 else False,
                'categories': categories,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(
                "spending_report_generated",
                user_id=user_id,
                period=period,
                total_spent=total_spent,
                total_budget=total_budget,
                categories_count=len(categories)
            )
            
            return report
            
        except Exception as e:
            logger.error("generate_spending_report_failed", error=str(e), user_id=user_id)
            raise




