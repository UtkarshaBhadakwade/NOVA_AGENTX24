import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated

def merge_lists(left: Optional[List[Any]], right: Optional[List[Any]]) -> List[Any]:
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right

class AgentState(TypedDict):
    """
    Shared State Schema for NOVA Agent Task 5 Adaptive Architecture.
    Tracks dynamic planning, parallel execution, hypothesis verification,
    conflicts, resource budgets, self-evaluation, and checkpointing.
    """
    objective: str
    timeframe: Optional[str]
    year: Optional[str]
    source_filter: Optional[str]
    quartile: Optional[str]
    
    # Adaptive Task 5 Fields
    plan: Annotated[List[Dict[str, Any]], merge_lists]
    pending_tasks: Annotated[List[str], merge_lists]
    completed_tasks: Annotated[List[str], merge_lists]
    active_agents: Annotated[List[str], merge_lists]
    
    current_task: Optional[str]
    delegated_agent: Optional[str]
    
    research_results: Annotated[List[Dict[str, Any]], merge_lists]
    market_results: Annotated[List[Dict[str, Any]], merge_lists]
    web_results: Annotated[List[Dict[str, Any]], merge_lists]
    crossref_results: Annotated[List[Dict[str, Any]], merge_lists]
    
    verification_results: Annotated[List[Dict[str, Any]], merge_lists]
    evidence_conflicts: Annotated[List[Dict[str, Any]], merge_lists]
    failed_tools: Annotated[List[str], merge_lists]
    fallback_attempts: Annotated[List[str], merge_lists]
    
    hypothesis: Optional[str]
    hypothesis_status: Optional[str]  # "SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "INSUFFICIENT_EVIDENCE"
    
    memory_context: Optional[Dict[str, Any]]
    confidence: Optional[str]  # "HIGH", "MEDIUM", "LOW"
    uncertainty: Optional[str]
    
    resource_budget: Optional[Dict[str, int]]
    replan_count: int
    loop_detected: bool
    self_eval_passed: bool
    data_availability_note: Optional[str]
    test_mode: Optional[str]  # "normal", "tool_failure", "conflict", "resource_constraint", "self_eval_fail"
    
    agent_findings: Annotated[List[Dict[str, Any]], merge_lists]
    agent_history: Annotated[List[str], merge_lists]
    actions_taken: Annotated[List[str], merge_lists]
    
    iteration_count: int
    max_iterations: int
    evidence_sufficient: bool
    task_complete: bool
    
    final_report: Optional[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]
    trace_events: Annotated[List[Dict[str, Any]], merge_lists]
    errors: Annotated[List[str], merge_lists]
    next_action: str
    search_query: str
    token_usage: Optional[Dict[str, Any]]
