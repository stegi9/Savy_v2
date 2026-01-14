"""
Financial calculation utilities.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import structlog

logger = structlog.get_logger()


def calculate_projected_balance(
    current_balance: float,
    upcoming_bills: List[Dict[str, Any]],
    estimated_spending: float = 0.0
) -> float:
    """
    Calculates projected end-of-month balance.
    
    Args:
        current_balance: Current account balance
        upcoming_bills: List of recurring bills
        estimated_spending: Estimated additional spending
        
    Returns:
        Projected balance
    """
    total_bills = sum(float(bill.get("amount", 0)) for bill in upcoming_bills)
    projected = current_balance - total_bills - estimated_spending
    return round(projected, 2)


def calculate_daily_spending_capacity(
    projected_balance: float,
    days_remaining: int = 30,
    safety_margin: float = 100.0
) -> float:
    """
    Calculates daily spending capacity.
    
    Args:
        projected_balance: Projected end-of-month balance
        days_remaining: Days remaining in month
        safety_margin: Minimum balance to maintain
        
    Returns:
        Daily spending capacity
    """
    available = projected_balance - safety_margin
    if available <= 0 or days_remaining <= 0:
        return 0.0
    
    daily_capacity = available / days_remaining
    return round(max(0.0, daily_capacity), 2)


def detect_bill_anomalies(
    current_bill: Dict[str, Any],
    historical_bills: List[Dict[str, Any]],
    threshold_percent: float = 15.0
) -> Dict[str, Any]:
    """
    Detects unusual increases in bill amounts.
    
    Args:
        current_bill: Current bill to check
        historical_bills: Previous bills of same type
        threshold_percent: Percentage increase to flag as anomaly
        
    Returns:
        Dict with anomaly detection result
    """
    if not historical_bills:
        return {"is_anomaly": False, "reason": "No historical data"}
    
    current_amount = float(current_bill.get("amount", 0))
    historical_amounts = [float(b.get("amount", 0)) for b in historical_bills]
    avg_historical = sum(historical_amounts) / len(historical_amounts)
    
    if avg_historical == 0:
        return {"is_anomaly": False, "reason": "Invalid historical data"}
    
    percent_change = ((current_amount - avg_historical) / avg_historical) * 100
    
    is_anomaly = percent_change > threshold_percent
    
    return {
        "is_anomaly": is_anomaly,
        "percent_change": round(percent_change, 2),
        "current_amount": current_amount,
        "average_amount": round(avg_historical, 2),
        "difference": round(current_amount - avg_historical, 2)
    }


def calculate_optimization_savings(
    current_cost: float,
    optimized_cost: float
) -> Dict[str, float]:
    """
    Calculates savings from optimization.
    
    Args:
        current_cost: Current bill amount
        optimized_cost: Optimized/suggested amount
        
    Returns:
        Dict with savings calculations
    """
    monthly_savings = current_cost - optimized_cost
    annual_savings = monthly_savings * 12
    percent_savings = (monthly_savings / current_cost * 100) if current_cost > 0 else 0
    
    return {
        "monthly_savings": round(monthly_savings, 2),
        "annual_savings": round(annual_savings, 2),
        "percent_savings": round(percent_savings, 2)
    }


def get_days_remaining_in_month() -> int:
    """
    Gets number of days remaining in current month.
    
    Returns:
        Days remaining
    """
    today = datetime.now()
    
    # Get last day of current month
    if today.month == 12:
        last_day = datetime(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
    
    days_remaining = (last_day.date() - today.date()).days + 1
    return max(1, days_remaining)


