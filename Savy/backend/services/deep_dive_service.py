"""
Service for deep dive analytics and AI insights.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import structlog
from dateutil.relativedelta import relativedelta

from repositories.report_repository import ReportRepository
from repositories.category_repository import CategoryRepository

logger = structlog.get_logger()


class DeepDiveService:
    """Service for advanced spending analytics."""
    
    def __init__(self, report_repository: ReportRepository, category_repository: CategoryRepository):
        self.report_repo = report_repository
        self.category_repo = category_repository
    
    def generate_deep_dive(
        self,
        user_id: str,
        period: str = "monthly",
        bank_account_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate deep dive analytics with AI insights.
        
        Args:
            user_id: User ID
            period: 'monthly', '3months', 'yearly'
            bank_account_id: Optional bank account ID
            
        Returns:
            Deep dive analytics data
        """
        try:
            # Calculate date ranges
            end_date = datetime.now()
            
            if period == "monthly":
                start_date = end_date.replace(day=1)
                previous_start = (start_date - relativedelta(months=1))
                previous_end = start_date - timedelta(days=1)
            elif period == "3months":
                start_date = end_date - relativedelta(months=3)
                previous_start = start_date - relativedelta(months=3)
                previous_end = start_date - timedelta(days=1)
            else:  # yearly
                start_date = end_date.replace(month=1, day=1)
                previous_start = start_date - relativedelta(years=1)
                previous_end = start_date - timedelta(days=1)
            
            # Get current period spending by category
            current_categories = self.report_repo.get_spending_by_category(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                bank_account_id=bank_account_id
            )
            
            # Get previous period spending by category
            previous_categories = self.report_repo.get_spending_by_category(
                user_id=user_id,
                start_date=previous_start,
                end_date=previous_end,
                bank_account_id=bank_account_id
            )
            
            # Create lookup for previous spending
            previous_lookup = {
                cat['category_id']: cat['total_spent']
                for cat in previous_categories
            }
            
            # Get total spent
            total_spent = sum(cat['total_spent'] for cat in current_categories)
            previous_total = sum(cat['total_spent'] for cat in previous_categories)
            
            # Get income
            total_income = self.report_repo.get_total_income(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                bank_account_id=bank_account_id
            )
            
            # Calculate spending velocity and projection
            days_in_period = (end_date - start_date).days
            days_elapsed = (datetime.now() - start_date).days
            
            if days_elapsed > 0:
                spending_velocity = (total_spent / days_elapsed) / (previous_total / days_in_period) if previous_total > 0 else 1.0
                projected_end_of_month = (total_spent / days_elapsed) * days_in_period
            else:
                spending_velocity = 1.0
                projected_end_of_month = total_spent
            
            # Build category comparisons with trends
            categories_comparison = []
            anomalies_detected = []
            
            for cat in current_categories:
                cat_id = cat['category_id']
                current_amount = cat['total_spent']
                previous_amount = previous_lookup.get(cat_id, 0.0)
                
                # Calculate change
                if previous_amount > 0:
                    change_percentage = ((current_amount - previous_amount) / previous_amount) * 100
                else:
                    change_percentage = 100.0 if current_amount > 0 else 0.0
                
                # Detect anomalies (>30% increase or >50% decrease)
                is_anomaly = (
                    (change_percentage > 30 and current_amount > 50) or
                    (change_percentage < -50 and previous_amount > 50)
                )
                
                if is_anomaly:
                    anomalies_detected.append({
                        'category_name': cat['category_name'],
                        'category_id': cat_id,
                        'change': change_percentage,
                        'current': current_amount,
                        'previous': previous_amount
                    })
                
                # Get trend data (last 30 days for monthly, or proportional)
                trend_start = max(start_date, end_date - timedelta(days=30))
                trend_data = self.report_repo.get_category_trend(
                    user_id=user_id,
                    category_id=cat_id,
                    start_date=trend_start,
                    end_date=end_date,
                    bank_account_id=bank_account_id
                )
                
                categories_comparison.append({
                    'category_id': cat_id,
                    'category_name': cat['category_name'],
                    'icon': cat.get('icon'),
                    'color': cat.get('color'),
                    'current_amount': current_amount,
                    'previous_amount': previous_amount,
                    'change_percentage': change_percentage,
                    'is_anomaly': is_anomaly,
                    'trend_data': trend_data
                })
            
            # Get cumulative spending data for current period
            current_cumulative = self.report_repo.get_daily_cumulative_spending(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                bank_account_id=bank_account_id
            )
            
            # Get cumulative spending data for previous period (for comparison)
            previous_cumulative = self.report_repo.get_daily_cumulative_spending(
                user_id=user_id,
                start_date=previous_start,
                end_date=previous_end,
                bank_account_id=bank_account_id
            )
            
            # Generate AI Insights
            ai_insights = self._generate_ai_insights(
                total_spent=total_spent,
                previous_total=previous_total,
                spending_velocity=spending_velocity,
                projected_end_of_month=projected_end_of_month,
                anomalies=anomalies_detected,
                net_balance=total_income - total_spent
            )
            
            return {
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_spent': total_spent,
                'total_income': total_income,
                'net_balance': total_income - total_spent,
                'previous_total_spent': previous_total,
                'spending_velocity': (spending_velocity - 1.0) * 100,  # Convert to percentage
                'projected_end_of_month': projected_end_of_month,
                'current_cumulative': current_cumulative,
                'previous_cumulative': previous_cumulative,
                'categories_comparison': categories_comparison,
                'ai_insights': ai_insights,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("generate_deep_dive_failed", error=str(e), user_id=user_id)
            raise
    
    def _generate_ai_insights(
        self,
        total_spent: float,
        previous_total: float,
        spending_velocity: float,
        projected_end_of_month: float,
        anomalies: List[Dict[str, Any]],
        net_balance: float
    ) -> List[Dict[str, Any]]:
        """
        Generate AI insights based on spending patterns.
        
        Returns:
            List of AI insight dictionaries
        """
        insights = []
        
        # Insight 1: Spending velocity
        velocity_change = (spending_velocity - 1.0) * 100
        if abs(velocity_change) > 10:
            insight_type = 'warning' if velocity_change > 0 else 'success'
            direction = 'più velocemente' if velocity_change > 0 else 'più lentamente'
            insights.append({
                'insight_type': insight_type,
                'title': f'Ritmo di spesa {"elevato" if velocity_change > 0 else "rallentato"}',
                'message': f'Stai spendendo il {abs(velocity_change):.1f}% {direction} rispetto al periodo precedente.',
                'category_id': None
            })
        
        # Insight 2: Projection warning
        if projected_end_of_month > total_spent * 1.2:
            insights.append({
                'insight_type': 'warning',
                'title': 'Proiezione spesa elevata',
                'message': f'Al ritmo attuale, la spesa proiettata è di €{projected_end_of_month:.2f}.',
                'category_id': None
            })
        
        # Insight 3: Category anomalies
        for anomaly in anomalies[:3]:  # Top 3 anomalies
            if anomaly['change'] > 0:
                insights.append({
                    'insight_type': 'warning',
                    'title': f'{anomaly["category_name"]}: spesa aumentata',
                    'message': f'Hai speso €{anomaly["current"]:.2f} (+{anomaly["change"]:.1f}% rispetto al periodo precedente).',
                    'category_id': anomaly['category_id']
                })
            else:
                insights.append({
                    'insight_type': 'success',
                    'title': f'{anomaly["category_name"]}: spesa ridotta',
                    'message': f'Hai risparmiato €{anomaly["previous"] - anomaly["current"]:.2f} ({abs(anomaly["change"]):.1f}% in meno).',
                    'category_id': anomaly['category_id']
                })
        
        # Insight 4: Net balance
        if net_balance > 0:
            insights.append({
                'insight_type': 'success',
                'title': 'Bilancio positivo',
                'message': f'Ottimo lavoro! Il tuo bilancio netto è di €{net_balance:.2f}.',
                'category_id': None
            })
        elif net_balance < -100:
            insights.append({
                'insight_type': 'warning',
                'title': 'Attenzione al bilancio',
                'message': f'Le tue uscite superano le entrate di €{abs(net_balance):.2f}.',
                'category_id': None
            })
        
        # If no insights, add a positive one
        if not insights:
            insights.append({
                'insight_type': 'info',
                'title': 'Tutto sotto controllo',
                'message': 'Le tue spese sono stabili rispetto al periodo precedente.',
                'category_id': None
            })
        
        return insights

