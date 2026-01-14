"""
Service layer for optimization opportunities.
"""
from typing import List, Dict, Any
import structlog
import random

from repositories.optimization_repository import OptimizationRepository

logger = structlog.get_logger()


class OptimizationService:
    """Business logic for bill optimization."""
    
    # Mock partners data (in production, this would come from external APIs)
    MOCK_PARTNERS = {
        'energy': [
            {'name': 'Enel Energia', 'discount': 0.15},
            {'name': 'Eni Plenitude', 'discount': 0.12},
            {'name': 'Sorgenia', 'discount': 0.18}
        ],
        'telco': [
            {'name': 'Fastweb', 'discount': 0.20},
            {'name': 'Iliad', 'discount': 0.25},
            {'name': 'ho.mobile', 'discount': 0.30}
        ],
        'gas': [
            {'name': 'Eni Gas', 'discount': 0.10},
            {'name': 'Iren', 'discount': 0.12}
        ],
        'insurance': [
            {'name': 'Linear', 'discount': 0.15},
            {'name': 'Genialloyd', 'discount': 0.20}
        ]
    }
    
    def __init__(self, optimization_repository: OptimizationRepository):
        self.optimization_repository = optimization_repository
    
    def scan_for_optimizations(
        self,
        user_id: str,
        categories: List[str] = None
    ) -> Dict[str, Any]:
        """
        Scan user's bills for optimization opportunities.
        
        Args:
            user_id: User ID
            categories: Optional list of categories to scan
            
        Returns:
            Dict with optimization opportunities and savings summary
        """
        try:
            # Default categories if not specified
            if not categories:
                categories = ['energy', 'telco', 'gas', 'insurance', 'subscriptions']
            
            logger.info("optimization_scan_started", user_id=user_id, categories=categories)
            
            # Get user's recurring bills
            bills = self.optimization_repository.get_user_bills(user_id, categories)
            
            if not bills:
                logger.info("optimization_scan_no_bills", user_id=user_id)
                return {
                    'optimizations': [],
                    'total_monthly_savings': 0.0,
                    'total_yearly_savings': 0.0,
                    'scanned_categories': categories,
                    'bills_scanned': 0,
                    'opportunities_found': 0,
                    'message': 'Nessuna bolletta trovata per le categorie selezionate.'
                }
            
            # Find optimization opportunities for each bill
            optimizations = []
            total_monthly_savings = 0.0
            
            for bill in bills:
                optimization = self._find_optimization_for_bill(bill, user_id)
                if optimization:
                    optimizations.append(optimization)
                    total_monthly_savings += optimization['savings_per_month']
            
            total_yearly_savings = total_monthly_savings * 12
            
            result = {
                'optimizations': optimizations,
                'total_monthly_savings': round(total_monthly_savings, 2),
                'total_yearly_savings': round(total_yearly_savings, 2),
                'scanned_categories': categories,
                'bills_scanned': len(bills),
                'opportunities_found': len(optimizations)
            }
            
            logger.info(
                "optimization_scan_completed",
                user_id=user_id,
                opportunities=len(optimizations),
                monthly_savings=total_monthly_savings
            )
            
            return result
            
        except Exception as e:
            logger.error("scan_for_optimizations_failed", error=str(e), user_id=user_id)
            raise
    
    def _find_optimization_for_bill(
        self,
        bill,
        user_id: str
    ) -> Dict[str, Any] | None:
        """
        Find optimization opportunity for a single bill.
        
        Args:
            bill: RecurringBill object
            user_id: User ID
            
        Returns:
            Dict with optimization details or None if no opportunity found
        """
        try:
            category = bill.category.lower() if bill.category else None
            
            # Get available partners for this category
            partners = self.MOCK_PARTNERS.get(category, [])
            if not partners:
                return None
            
            # Select best partner (random for MVP, in production use real comparison)
            best_partner = random.choice(partners)
            
            current_cost = float(bill.amount)
            discount = best_partner['discount']
            optimized_cost = current_cost * (1 - discount)
            savings_per_month = current_cost - optimized_cost
            
            # Only suggest if savings are significant (>5€/month)
            if savings_per_month < 5.0:
                return None
            
            # Create optimization lead in database
            lead = self.optimization_repository.create_optimization_lead(
                user_id=user_id,
                bill_id=bill.id,
                current_cost=current_cost,
                optimized_cost=optimized_cost,
                partner_name=best_partner['name'],
                bill_category=bill.category,
                partner_offer_details=f"Sconto {int(discount * 100)}% sul piano attuale"
            )
            
            return {
                'id': lead.id,
                'bill_category': bill.category,
                'bill_name': bill.name,
                'current_provider': bill.provider or 'Attuale',
                'current_cost': round(current_cost, 2),
                'recommended_provider': best_partner['name'],
                'optimized_cost': round(optimized_cost, 2),
                'savings_per_month': round(savings_per_month, 2),
                'savings_per_year': round(savings_per_month * 12, 2),
                'discount_percentage': int(discount * 100),
                'partner_offer_url': f"https://example.com/{best_partner['name'].lower().replace(' ', '-')}",
                'confidence': 0.85  # High confidence for MVP
            }
            
        except Exception as e:
            logger.error("find_optimization_for_bill_failed", error=str(e), bill_id=bill.id)
            return None
    
    def get_user_optimization_leads(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all optimization leads for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of optimization leads
        """
        try:
            leads = self.optimization_repository.get_user_optimization_leads(user_id)
            
            # Convert to dict format
            result = []
            for lead in leads:
                result.append({
                    'id': lead.id,
                    'bill_category': lead.bill_category,
                    'current_cost': float(lead.current_cost),
                    'optimized_cost': float(lead.optimized_cost),
                    'savings_amount': float(lead.savings_amount),
                    'partner_name': lead.partner_name,
                    'status': lead.status,
                    'created_at': lead.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error("get_user_optimization_leads_failed", error=str(e), user_id=user_id)
            raise





