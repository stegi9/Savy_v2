"""
Node: Format Response
Formats the final response for the API endpoint.
"""
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


async def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the agent's output into a structured response.
    
    Prepares the final JSON response with:
    - Decision (affordable/caution/not_affordable)
    - Reasoning from LLM
    - Optimization leads (if any)
    
    Args:
        state: Final agent state
        
    Returns:
        State with formatted messages
    """
    logger.info("format_response_started")
    
    try:
        # Add assistant message to conversation history
        assistant_message = {
            "role": "assistant",
            "content": state.get("reasoning", ""),
            "decision": state.get("decision", ""),
            "optimization_leads_count": len(state.get("optimization_leads", []))
        }
        
        messages = state.get("messages", [])
        messages.append(assistant_message)
        state["messages"] = messages
        
        logger.info(
            "format_response_completed",
            decision=state.get("decision"),
            has_optimizations=len(state.get("optimization_leads", [])) > 0
        )
        
        return state
        
    except Exception as e:
        logger.error("format_response_failed", error=str(e))
        return state






