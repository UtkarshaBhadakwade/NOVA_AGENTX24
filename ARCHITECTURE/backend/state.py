from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    State definition for the Competitive Intelligence Agent ReAct loop.
    """
    objective: str                             # The objective or query provided by the user
    collected_evidence: List[Dict[str, Any]]   # Raw documents/snippets fetched from web/research search
    analysis_result: Optional[Dict[str, Any]]  # Output of the analyze_information tool
    steps: List[Dict[str, Any]]                # Safe agent trace events exposed to frontend/logs
    iterations: int                            # Count of currently executed ReAct iterations
    max_iterations: int                        # Maximum allowed iterations (default: 8)
    next_action: Optional[str]                 # The action selected by the reasoning engine (web_search, etc.)
    next_action_input: Optional[str]           # Input argument for the next action
    final_report: Optional[str]                # The compiled structured markdown report
    error: Optional[str]                       # Captured error messages for error handling
