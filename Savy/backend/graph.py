"""
LangGraph StateGraph definition for the AI Financial Coach.
This is the core orchestration logic for the agent.
"""
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import structlog

logger = structlog.get_logger()


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    State for the financial coach agent.
    This state is passed between all nodes in the graph.
    """
    user_id: str
    balance: float
    upcoming_bills: List[Dict[str, Any]]
    user_query: str
    analysis_result: Dict[str, Any]
    decision: str
    reasoning: str
    optimization_leads: List[Dict[str, Any]]
    affiliate_offers: List[Dict[str, Any]] # ADDED
    messages: List[Dict[str, str]]


# ============================================================================
# GRAPH CREATION
# ============================================================================

def create_graph() -> StateGraph:
    """
    Creates and returns the LangGraph StateGraph for the financial coach.
    
    Graph flow (FIXED - Sequential to avoid state merge issues):
    START → fetch_user_data → financial_analysis → affiliate_search 
          → coach_reasoning → optimizer_check → format_response → END
    
    Note: Affiliate search runs after financial analysis to avoid
    parallel edge convergence issues in LangGraph.
    """
    from nodes.fetch_data import fetch_user_data
    from nodes.financial_analysis import financial_analysis
    from nodes.coach_reasoning import coach_reasoning
    from nodes.optimizer_check import optimizer_check
    from nodes.format_response import format_response
    from nodes.affiliate_node import AffiliateNode
    
    affiliate_node = AffiliateNode()

    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("fetch_user_data", fetch_user_data)
    workflow.add_node("financial_analysis", financial_analysis)
    workflow.add_node("affiliate_search", affiliate_node.run)
    workflow.add_node("coach_reasoning", coach_reasoning)
    workflow.add_node("optimizer_check", optimizer_check)
    workflow.add_node("format_response", format_response)
    
    # Define edges (Sequential to avoid convergence issues)
    workflow.set_entry_point("fetch_user_data")
    workflow.add_edge("fetch_user_data", "financial_analysis")
    workflow.add_edge("financial_analysis", "affiliate_search")
    workflow.add_edge("affiliate_search", "coach_reasoning")
    workflow.add_edge("coach_reasoning", "optimizer_check")
    workflow.add_edge("optimizer_check", "format_response")
    workflow.add_edge("format_response", END)
    
    logger.info("langgraph_initialized", nodes=6, flow="sequential")
    
    return workflow.compile()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def invoke_agent(user_id: str, user_query: str) -> AgentState:
    """
    High-level function to invoke the agent graph.
    
    Args:
        user_id: User UUID
        user_query: User's financial question
        
    Returns:
        Final state after graph execution
    """
    graph = create_graph()
    
    initial_state: AgentState = {
        "user_id": user_id,
        "balance": 0.0,
        "upcoming_bills": [],
        "user_query": user_query,
        "analysis_result": {},
        "decision": "",
        "reasoning": "",
        "optimization_leads": [],
        "affiliate_offers": [], # DEFAULT
        "messages": []
    }
    
    logger.info("agent_invocation_started", user_id=user_id, query=user_query)
    
    try:
        result = await graph.ainvoke(initial_state)
        logger.info("agent_invocation_completed", user_id=user_id, decision=result.get("decision"))
        return result
    except Exception as e:
        logger.error("agent_invocation_failed", user_id=user_id, error=str(e))
        raise






