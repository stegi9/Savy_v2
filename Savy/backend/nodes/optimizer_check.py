"""
Node: Optimizer Check
Identifies optimization opportunities for recurring bills.
"""
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


async def optimizer_check(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Checks for optimization opportunities in user's bills.
    
    Identifies bills that could be optimized:
    - Energy: Compare with alternative providers
    - Telco: Check for better plans
    - Subscriptions: Identify unused services
    
    Args:
        state: Current agent state with bills
        
    Returns:
        Updated state with optimization_leads
    """
    upcoming_bills = state.get("upcoming_bills", [])
    
    logger.info("optimizer_check_started", bills_count=len(upcoming_bills))
    
    try:
        optimization_leads = []
        
        # Check each bill for optimization potential
        for bill in upcoming_bills:
            category = bill.get("category", "")
            current_amount = float(bill.get("amount", 0))
            
            # Simple optimization logic (will be enhanced with real partner APIs)
            if category == "energy" and current_amount > 80:
                # Mock energy optimization
                optimized_amount = current_amount * 0.75  # 25% savings
                optimization_leads.append({
                    "bill_id": bill.get("id"),
                    "bill_category": category,
                    "current_cost": current_amount,
                    "optimized_cost": optimized_amount,
                    "partner_name": "Sorgenia Green",
                    "partner_offer_details": "Piano Eco+ con sconto 25% primo anno",
                    "savings_amount": current_amount - optimized_amount
                })
            
            elif category == "telco" and current_amount > 35:
                # Mock telco optimization
                optimized_amount = current_amount * 0.80  # 20% savings
                optimization_leads.append({
                    "bill_id": bill.get("id"),
                    "bill_category": category,
                    "current_cost": current_amount,
                    "optimized_cost": optimized_amount,
                    "partner_name": "Iliad Fiber",
                    "partner_offer_details": "Fibra illimitata + mobile 100GB",
                    "savings_amount": current_amount - optimized_amount
                })
        
        state["optimization_leads"] = optimization_leads
        
        logger.info(
            "optimizer_check_completed",
            leads_found=len(optimization_leads),
            potential_savings=sum(lead.get("savings_amount", 0) for lead in optimization_leads)
        )
        
        return state
        
    except Exception as e:
        logger.error("optimizer_check_failed", error=str(e))
        state["optimization_leads"] = []
        return state






