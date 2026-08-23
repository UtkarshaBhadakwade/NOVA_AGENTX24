import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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

from backend.observability.tracer import NOVAObservabilityTracer

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_agent.main")

# Initialize SQLite database safely
try:
    init_db()
except Exception as e:
    logger.warning(f"[MEMORY_WARNING] Persistent memory storage unavailable. Details: {str(e)}")

app = FastAPI(
    title="NOVA Agent - Autonomous Competitive Intelligence System",
    description="Powered by LangGraph Adaptive Multi-Agent Architecture, Checkpointing, Gemini 3.6 Flash, Tavily, arXiv, and CrossRef.",
    version="2.0.0"
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
    test_mode: Optional[str] = Field("normal", description="Adversarial test mode: normal, tool_failure, conflict, resource_constraint, self_eval_fail")

class AnalyzeResponse(BaseModel):
    id: Optional[str] = None
    objective: str
    status: str = "completed"
    iterations: int = 0
    tools_called: List[str] = []
    trace_events: List[Dict[str, Any]] = []
    final_report: Optional[Dict[str, Any]] = None
    web_results_count: int = 0
    research_results_count: int = 0
    crossref_results_count: int = 0
    memory_found: bool = False
    errors: List[str] = []
    token_usage: Optional[Dict[str, Any]] = None

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "NOVA Agent Adaptive Multi-Agent Framework (Task 5)",
        "gemini_api_key_configured": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
        "tavily_api_key_configured": bool(os.environ.get("TAVILY_API_KEY"))
    }

@app.get("/investigations")
def list_investigations(limit: int = Query(50, ge=1, le=200)):
    """Returns past saved investigations grouped into pinned and recent lists."""
    try:
        return get_investigations(limit=limit)
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] List investigations warning: {str(e)}")
        return {"pinned": [], "recent": []}

@app.get("/investigations/search")
def search_history(q: str = Query(..., min_length=1)):
    """Searches past investigations by objective title or report content."""
    try:
        return search_investigations(q)
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Search history warning: {str(e)}")
        return []

@app.get("/investigations/{investigation_id}")
def get_investigation(investigation_id: str):
    """Retrieves full details and report for a specific saved investigation."""
    try:
        inv = get_investigation_by_id(investigation_id)
        if not inv:
            raise HTTPException(status_code=404, detail="Investigation not found.")
        return inv
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Get investigation warning: {str(e)}")
        raise HTTPException(status_code=404, detail="Investigation memory unavailable.")

@app.post("/investigations/{investigation_id}/pin")
def pin_investigation(investigation_id: str):
    """Toggles pinned status for a saved investigation item."""
    try:
        pinned = toggle_pinned(investigation_id)
        return {"id": investigation_id, "pinned": pinned}
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Pin investigation warning: {str(e)}")
        return {"id": investigation_id, "pinned": False}

@app.post("/analyze", response_model=AnalyzeResponse)
def run_intelligence_analysis(request: AnalyzeRequest):
    if not request.objective.strip():
        raise HTTPException(status_code=400, detail="Objective string cannot be empty.")

    # Memory Retrieval: Search relevant past investigations
    memory_context = None
    memory_found = False
    try:
        past_invs = search_investigations(request.objective)
        if past_invs:
            memory_found = True
            top_match = past_invs[0]
            memory_context = {
                "id": top_match.get("id"),
                "objective": top_match.get("objective"),
                "created_at": top_match.get("created_at")
            }
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Memory retrieval warning: {str(e)}")

    initial_trace = []
    if memory_found and memory_context:
        initial_trace.append({"event": "[MEMORY_RETRIEVAL]", "detail": f"Searching past investigations for '{request.objective[:40]}...'"})
        initial_trace.append({"event": "[MEMORY_FOUND]", "detail": f"Loaded past investigation context: '{memory_context['objective'][:40]}...'"})

    thread_id = str(uuid.uuid4())[:8]

    initial_state: AgentState = {
        "objective": request.objective,
        "timeframe": "Latest",
        "year": "Any Year",
        "source_filter": "All Sources",
        "quartile": "All Quartiles",
        "plan": [],
        "pending_tasks": [],
        "completed_tasks": [],
        "active_agents": [],
        "current_task": None,
        "delegated_agent": None,
        "research_results": [],
        "market_results": [],
        "web_results": [],
        "crossref_results": [],
        "verification_results": [],
        "evidence_conflicts": [],
        "failed_tools": [],
        "fallback_attempts": [],
        "hypothesis": None,
        "hypothesis_status": None,
        "memory_context": memory_context,
        "confidence": None,
        "uncertainty": None,
        "resource_budget": {"max_iterations": MAX_ITERATIONS},
        "replan_count": 0,
        "loop_detected": False,
        "self_eval_passed": False,
        "data_availability_note": None,
        "test_mode": request.test_mode or "normal",
        "agent_findings": [],
        "agent_history": [],
        "actions_taken": [],
        "iteration_count": 0,
        "max_iterations": MAX_ITERATIONS,
        "evidence_sufficient": False,
        "task_complete": False,
        "final_report": None,
        "analysis_results": None,
        "trace_events": initial_trace,
        "errors": [],
        "next_action": "supervisor",
        "search_query": request.objective
    }

    logger.info(f"Starting Task 5 Adaptive Agent Graph for objective: '{request.objective}' (TestMode: {request.test_mode})")
    
    try:
        tracer = NOVAObservabilityTracer(investigation_id=thread_id)
        final_state = agent_graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}, "callbacks": [tracer]}
        )

        tools_called = [
            action for action in final_state.get("actions_taken", [])
            if not action.startswith("supervisor ->")
        ]

        web_res = final_state.get("market_results", []) or final_state.get("web_results", [])

        final_trace = final_state.get("trace_events", [])
        final_trace.append({
            "event": "[CHECKPOINT]",
            "detail": f"LangGraph state checkpointed under thread_id '{thread_id}'."
        })

        response_data = {
            "id": None,
            "objective": final_state["objective"],
            "status": "completed" if final_state.get("task_complete") else "incomplete",
            "iterations": final_state.get("iteration_count", 0),
            "tools_called": tools_called,
            "trace_events": final_trace,
            "final_report": final_state.get("final_report"),
            "web_results_count": len(web_res),
            "research_results_count": len(final_state.get("research_results", [])),
            "crossref_results_count": len(final_state.get("crossref_results", [])),
            "memory_found": memory_found,
            "errors": final_state.get("errors", []),
            "token_usage": tracer.token_usage
        }

        try:
            saved = save_investigation(response_data)
            if saved and isinstance(saved, dict):
                response_data["id"] = saved.get("id")
        except Exception as db_err:
            logger.warning(f"[MEMORY_WARNING] Memory save warning: {str(db_err)}")

        return AnalyzeResponse(**response_data)

    except Exception as e:
        logger.error(f"Error executing agent graph: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "stage": "agent_execution",
                "message": f"Agent execution encountered an error: {str(e)}"
            }
        )

# Mount static frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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
        root_path = os.path.join(root_dir, file_name)
        if os.path.exists(root_path):
            return FileResponse(root_path)
        raise HTTPException(status_code=404, detail="File not found")
