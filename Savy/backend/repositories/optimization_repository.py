"""
Repository for optimization leads.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import structlog

from models.optimization_lead import OptimizationLead
from models.recurring_bill import RecurringBill

logger = structlog.get_logger()


class OptimizationRepository:
    """Repository for optimization leads operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_bills(self, user_id: str, categories: Optional[List[str]] = None) -> List[RecurringBill]:
        """
        Get user's recurring bills.
        
        Args:
            user_id: User ID
            categories: Optional list of categories to filter by
            
        Returns:
            List of recurring bills
        """
        try:
            query = self.db.query(RecurringBill).filter(
                RecurringBill.user_id == user_id,
                RecurringBill.is_active == True
            )
            
            if categories:
                query = query.filter(RecurringBill.category.in_(categories))
            
            bills = query.all()
            
            logger.info(
                "user_bills_retrieved",
                user_id=user_id,
                count=len(bills)
            )
            
            return bills
            
        except Exception as e:
            logger.error("get_user_bills_failed", error=str(e), user_id=user_id)
            raise
    
    def create_optimization_lead(
        self,
        user_id: str,
        bill_id: str,
        current_cost: float,
        optimized_cost: float,
        partner_name: str,
        bill_category: str,
        partner_offer_details: Optional[str] = None
    ) -> OptimizationLead:
        """
        Create a new optimization lead.
        
        Args:
            user_id: User ID
            bill_id: Recurring bill ID
            current_cost: Current monthly cost
            optimized_cost: Optimized monthly cost
            partner_name: Partner/provider name
            bill_category: Bill category
            partner_offer_details: Optional offer details
            
        Returns:
            Created OptimizationLead
        """
        try:
            savings_amount = current_cost - optimized_cost
            
            lead = OptimizationLead(
                user_id=user_id,
                bill_id=bill_id,
                current_cost=current_cost,
                optimized_cost=optimized_cost,
                savings_amount=savings_amount,
                partner_name=partner_name,
                bill_category=bill_category,
                partner_offer_details=partner_offer_details,
                status='pending'
            )
            
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(
                "optimization_lead_created",
                lead_id=lead.id,
                user_id=user_id,
                savings=savings_amount
            )
            
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error("create_optimization_lead_failed", error=str(e), user_id=user_id)
            raise
    
    def get_user_optimization_leads(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[OptimizationLead]:
        """
        Get optimization leads for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter ('pending', 'accepted', 'rejected')
            
        Returns:
            List of optimization leads
        """
        try:
            query = self.db.query(OptimizationLead).filter(
                OptimizationLead.user_id == user_id
            )
            
            if status:
                query = query.filter(OptimizationLead.status == status)
            
            leads = query.order_by(OptimizationLead.created_at.desc()).all()
            
            logger.info(
                "optimization_leads_retrieved",
                user_id=user_id,
                count=len(leads)
            )
            
            return leads
            
        except Exception as e:
            logger.error("get_user_optimization_leads_failed", error=str(e), user_id=user_id)
            raise
    
    def update_lead_status(self, lead_id: str, status: str) -> OptimizationLead:
        """
        Update optimization lead status.
        
        Args:
            lead_id: Lead ID
            status: New status
            
        Returns:
            Updated lead
        """
        try:
            lead = self.db.query(OptimizationLead).filter(
                OptimizationLead.id == lead_id
            ).first()
            
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")
            
            lead.status = status
            self.db.commit()
            self.db.refresh(lead)
            
            logger.info(
                "optimization_lead_status_updated",
                lead_id=lead_id,
                status=status
            )
            
            return lead
            
        except Exception as e:
            self.db.rollback()
            logger.error("update_lead_status_failed", error=str(e), lead_id=lead_id)
            raise



