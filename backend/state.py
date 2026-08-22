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
    Shared State Schema for NOVA Agent Multi-Agent System.
    Tracks delegation, findings, trace events, and report state across graph loops.
    """
    objective: str
    timeframe: Optional[str]
    year: Optional[str]
    source_filter: Optional[str]
    quartile: Optional[str]
    current_task: Optional[str]
    delegated_agent: Optional[str]
    research_results: Annotated[List[Dict[str, Any]], merge_lists]
    market_results: Annotated[List[Dict[str, Any]], merge_lists]
    web_results: Annotated[List[Dict[str, Any]], merge_lists]
    crossref_results: Annotated[List[Dict[str, Any]], merge_lists]
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
