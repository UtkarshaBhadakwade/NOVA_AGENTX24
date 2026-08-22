import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from backend.agent import agent_graph, MAX_ITERATIONS
from backend.state import AgentState

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_agent.main")

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

class AnalyzeResponse(BaseModel):
    objective: str
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

@app.post("/analyze", response_model=AnalyzeResponse)
def run_intelligence_analysis(request: AnalyzeRequest):
    if not request.objective.strip():
        raise HTTPException(status_code=400, detail="Objective string cannot be empty.")

    initial_state: AgentState = {
        "objective": request.objective,
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

    logger.info(f"Starting NOVA Agent Multi-Agent run for objective: '{request.objective}'")
    try:
        final_state = agent_graph.invoke(initial_state)

        # Extract tools/agents called from actions_taken
        tools_called = [
            action for action in final_state.get("actions_taken", [])
            if not action.startswith("supervisor ->")
        ]

        web_res = final_state.get("market_results", []) or final_state.get("web_results", [])

        return AnalyzeResponse(
            objective=final_state["objective"],
            status="completed" if final_state.get("task_complete") else "incomplete",
            iterations=final_state.get("iteration_count", 0),
            tools_called=tools_called,
            trace_events=final_state.get("trace_events", []),
            final_report=final_state.get("final_report"),
            web_results_count=len(web_res),
            research_results_count=len(final_state.get("research_results", [])),
            crossref_results_count=len(final_state.get("crossref_results", [])),
            errors=final_state.get("errors", [])
        )
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
