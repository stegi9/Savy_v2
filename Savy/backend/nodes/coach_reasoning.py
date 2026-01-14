"""
Node: Coach Reasoning (LLM)
Uses LLM to provide personalized financial advice based on analysis.
"""
from typing import Dict, Any
import structlog
import json

logger = structlog.get_logger()


async def coach_reasoning(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses LLM to reason about the user's financial query.
    
    The LLM receives:
    - User's question
    - Financial analysis results
    - Context about bills and balance
    
    Returns decision: affordable, caution, not_affordable
    
    Args:
        state: Current agent state with analysis
        
    Returns:
        Updated state with decision and reasoning
    """
    user_query = state.get("user_query", "")
    analysis = state.get("analysis_result", {})
    
    logger.info("coach_reasoning_started", query=user_query)
    
    try:
        # Use LLM for intelligent reasoning
        from services.llm_service import get_financial_advice
        
        result = await get_financial_advice(user_query, analysis)
        
        state["decision"] = result.get("decision", "caution")
        state["reasoning"] = result.get("reasoning", "Non riesco ad analizzare la tua situazione.")
        
        logger.info("coach_reasoning_completed", decision=state["decision"])
        
        return state
        
    except Exception as e:
        logger.error("coach_reasoning_failed", error=str(e))
        
        # Fallback to simple logic if LLM fails
        projected_balance = analysis.get("projected_balance", 0)
        
        if projected_balance < 200:
            decision = "not_affordable"
            reasoning = f"Situazione critica: saldo previsto €{projected_balance:.2f}. Evita spese non essenziali."
        elif projected_balance < 500:
            decision = "caution"
            reasoning = f"Attenzione: saldo previsto €{projected_balance:.2f}. Limita le spese."
        else:
            decision = "affordable"
            reasoning = f"Situazione stabile: saldo previsto €{projected_balance:.2f}."
        
        state["decision"] = decision
        state["reasoning"] = reasoning
        
        return state


