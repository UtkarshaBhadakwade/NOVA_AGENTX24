import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from backend.agent import agent_graph, MAX_ITERATIONS
from backend.state import AgentState
from backend.db import (
    init_db,
    save_investigation,
    get_investigations,
    get_investigation_by_id,
    search_investigations,
    toggle_pinned
)

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_agent.main")

# Initialize SQLite database on startup
init_db()

app = FastAPI(
    title="NOVA Agent - Autonomous Competitive Intelligence Agent",
    description="Powered by LangGraph Multi-Agent Architecture, Gemini 3.6 Flash, Tavily, arXiv, and CrossRef.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    objective: str = Field(
        ...,
        description="The intelligence objective to gather information and report on.",
        example="Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization."
    )
    timeframe: Optional[str] = Field("Latest", description="Timeframe filter")
    year: Optional[str] = Field("Any Year", description="Publication year filter")
    source_filter: Optional[str] = Field("All Sources", description="Source filter")
    quartile: Optional[str] = Field("All Quartiles", description="Journal Quartile filter (Q1, Q2, Q3, Q4)")

class AnalyzeResponse(BaseModel):
    id: Optional[str]
    objective: str
    timeframe: str
    year: str
    source_filter: str
    quartile: str
    status: str
    iterations: int
    tools_called: List[str]
    trace_events: List[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    web_results_count: int
    research_results_count: int
    crossref_results_count: int
    errors: List[str]

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "NOVA Agent Autonomous Multi-Agent System"}

@app.get("/investigations")
def list_investigations(limit: int = Query(50, ge=1, le=200)):
    """Returns past saved investigations grouped into pinned and recent lists."""
    return get_investigations(limit=limit)

@app.get("/investigations/search")
def search_history(q: str = Query(..., min_length=1)):
    """Searches past investigations by objective title or report content."""
    return search_investigations(q)

@app.get("/investigations/{investigation_id}")
def get_investigation(investigation_id: str):
    """Retrieves full details and report for a specific saved investigation."""
    inv = get_investigation_by_id(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return inv

@app.post("/investigations/{investigation_id}/pin")
def pin_investigation(investigation_id: str):
    """Toggles pinned status for a saved investigation item."""
    pinned = toggle_pinned(investigation_id)
    return {"id": investigation_id, "pinned": pinned}

@app.post("/analyze", response_model=AnalyzeResponse)
def run_intelligence_analysis(request: AnalyzeRequest):
    if not request.objective.strip():
        raise HTTPException(status_code=400, detail="Objective string cannot be empty.")

    initial_state: AgentState = {
        "objective": request.objective,
        "timeframe": request.timeframe or "Latest",
        "year": request.year or "Any Year",
        "source_filter": request.source_filter or "All Sources",
        "quartile": request.quartile or "All Quartiles",
        "current_task": None,
        "delegated_agent": None,
        "research_results": [],
        "market_results": [],
        "web_results": [],
        "crossref_results": [],
        "agent_findings": [],
        "agent_history": [],
        "actions_taken": [],
        "iteration_count": 0,
        "max_iterations": MAX_ITERATIONS,
        "evidence_sufficient": False,
        "task_complete": False,
        "final_report": None,
        "analysis_results": None,
        "trace_events": [],
        "errors": [],
        "next_action": "supervisor",
        "search_query": request.objective
    }

    logger.info(f"Starting NOVA Agent Multi-Agent run for objective: '{request.objective}' (Year: {request.year}, Quartile: {request.quartile})")
    try:
        final_state = agent_graph.invoke(initial_state)

        tools_called = [
            action for action in final_state.get("actions_taken", [])
            if not action.startswith("supervisor ->")
        ]

        web_res = final_state.get("market_results", []) or final_state.get("web_results", [])

        response_data = {
            "objective": final_state["objective"],
            "timeframe": request.timeframe or "Latest",
            "year": request.year or "Any Year",
            "source_filter": request.source_filter or "All Sources",
            "quartile": request.quartile or "All Quartiles",
            "status": "completed" if final_state.get("task_complete") else "incomplete",
            "iterations": final_state.get("iteration_count", 0),
            "tools_called": tools_called,
            "trace_events": final_state.get("trace_events", []),
            "final_report": final_state.get("final_report"),
            "web_results_count": len(web_res),
            "research_results_count": len(final_state.get("research_results", [])),
            "crossref_results_count": len(final_state.get("crossref_results", [])),
            "errors": final_state.get("errors", [])
        }

        saved = save_investigation(response_data)
        response_data["id"] = saved.get("id")

        return AnalyzeResponse(**response_data)
    except Exception as e:
        logger.error(f"Error executing agent graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

# Mount static frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
    
    @app.get("/{file_name}")
    def serve_static_files(file_name: str):
        file_path = os.path.join(frontend_dir, file_name)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="File not found")
