"""
Node: Financial Analysis
Performs financial calculations and projections.
"""
from typing import Dict, Any
import structlog
from datetime import datetime
from decimal import Decimal

logger = structlog.get_logger()


async def financial_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes user's financial situation.
    
    Calculates:
    - Projected end-of-month balance
    - Total upcoming bills amount
    - Risk assessment (is balance sufficient?)
    - Spending capacity
    
    Args:
        state: Current agent state with balance and bills
        
    Returns:
        Updated state with analysis_result
    """
    balance = state.get("balance", 0.0)
    upcoming_bills = state.get("upcoming_bills", [])
    
    logger.info("financial_analysis_started", balance=balance, bills_count=len(upcoming_bills))
    
    try:
        # Calculate total bills
        total_bills = sum(float(bill.get("amount", 0)) for bill in upcoming_bills)
        
        # Project end-of-month balance
        projected_balance = balance - total_bills
        
        # Risk assessment
        at_risk = projected_balance < 100.0  # Less than 100€ safety margin
        
        # Calculate daily spending capacity (assuming 30 days)
        days_in_month = 30
        daily_capacity = projected_balance / days_in_month if projected_balance > 0 else 0
        
        analysis_result = {
            "current_balance": float(balance),
            "total_bills": float(total_bills),
            "projected_balance": float(projected_balance),
            "at_risk": at_risk,
            "daily_spending_capacity": float(daily_capacity),
            "bills_breakdown": upcoming_bills
        }
        
        # Return ONLY the update, not the full state
        return {"analysis_result": analysis_result}
        
    except Exception as e:
        logger.error("financial_analysis_failed", error=str(e))
        return {
            "analysis_result": {
                "error": str(e),
                "at_risk": True
            }
        }






