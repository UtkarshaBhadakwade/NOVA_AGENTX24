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
    LangGraph state schema for Agent X Competitive Intelligence Agent.
    Uses list merge reducers to persist trace events, results, and actions across graph steps.
    """
    objective: str
    web_results: Annotated[List[Dict[str, Any]], merge_lists]
    research_results: Annotated[List[Dict[str, Any]], merge_lists]
    analysis_results: Optional[Dict[str, Any]]
    actions_taken: Annotated[List[str], merge_lists]
    iteration_count: int
    max_iterations: int
    task_complete: bool
    final_report: Optional[Dict[str, Any]]
    trace_events: Annotated[List[Dict[str, Any]], merge_lists]
    errors: Annotated[List[str], merge_lists]
    next_action: str
    search_query: str
