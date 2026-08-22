import logging
from typing import Dict, Any
from backend.state import AgentState
from backend.tools import research_search, crossref_search

logger = logging.getLogger("nova_agent.research_agent")

def research_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    RESEARCH AGENT
    Role: Scientific and Technical Intelligence Specialist.
    
    Responsibilities:
    - Queries arXiv REST API for scientific papers.
    - Queries CrossRef REST API for peer-reviewed journal publications and DOIs.
    - Collects technical evidence and returns structured findings to shared state.
    """
    query = state.get("search_query", state["objective"])
    
    new_trace_events = [
        {
            "event": "[RESEARCH_AGENT]",
            "detail": f"Searching scientific and technical evidence on arXiv & CrossRef for: '{query}'"
        }
    ]
    
    arxiv_results = []
    crossref_results = []
    errors = []
    
    try:
        arxiv_results = research_search(query)
    except Exception as e:
        logger.error(f"ResearchAgent arXiv error: {str(e)}")
        errors.append(f"arXiv Search Warning: {str(e)}")
        
    try:
        crossref_results = crossref_search(query)
    except Exception as e:
        logger.error(f"ResearchAgent CrossRef error: {str(e)}")
        errors.append(f"CrossRef Search Warning: {str(e)}")

    valid_arxiv = [r for r in arxiv_results if r.get("title") != "Research Search Execution Failure"]
    valid_crossref = [r for r in crossref_results if r.get("title") != "CrossRef Search Execution Failure"]
    
    total_found = len(valid_arxiv) + len(valid_crossref)

    new_trace_events.append({
        "event": "[TOOL_RESULT]",
        "detail": f"Research findings collected: {len(valid_arxiv)} arXiv papers and {len(valid_crossref)} CrossRef publications."
    })

    findings_summary = {
        "agent": "ResearchAgent",
        "query": query,
        "arxiv_count": len(valid_arxiv),
        "crossref_count": len(valid_crossref),
        "top_titles": [r.get("title") for r in (valid_arxiv + valid_crossref)[:4]]
    }

    return {
        "research_results": arxiv_results,
        "crossref_results": crossref_results,
        "agent_findings": [findings_summary],
        "actions_taken": [f"ResearchAgent (arXiv: {len(valid_arxiv)}, CrossRef: {len(valid_crossref)})"],
        "agent_history": ["ResearchAgent"],
        "trace_events": new_trace_events,
        "errors": errors
    }
