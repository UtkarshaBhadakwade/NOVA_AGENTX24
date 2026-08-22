# Competitive Intelligence Agent - Backend MVP

An autonomous, agentic system designed to monitor and synthesize competitive intelligence (research papers, patents, competitor activities, industry news, and emerging trends) using a ReAct-style loop built with **LangGraph**, **LangChain**, **Gemini API**, and **FastAPI**.

## Features
* **ReAct Reasoning Loop**: The agent dynamically reasons about missing information, selects and executes search/analysis tools, and continues until it has sufficient evidence to answer the objective.
* **Academic and Web Research Tools**: Direct integration with arXiv API for academic papers and Tavily API for real-time web searches.
* **Structured Analysis**: Leverages Gemini's structured output function-calling engine to classify threats, opportunities, and trends.
* **Safe Agent Trace Events**: Exposes high-level execution step events (`REASONING_STATUS`, `ACTION`, `TOOL_RESULT`, `DECISION`, `TASK_COMPLETE`) without exposing raw, internal chain-of-thought details.
* **Robust Error Handling**: Handles API failures, empty search results, tool crashes, and enforces a maximum loop iteration limit (default: 8) to prevent runaway execution.

---

## File Structure

```text
backend/
├── main.py                  # FastAPI application entry point
├── agent.py                 # LangGraph ReAct state machine definition
├── state.py                 # AgentState TypedDict schema
├── requirements.txt         # Python project dependencies
├── test_agent.py            # Local agent simulation test script
└── tools/
    ├── web_search.py        # Web search wrapper using Tavily
    ├── research_search.py   # Scholarly search wrapper using arXiv
    └── analyze.py           # Structured intelligence analysis using Gemini
.env.example                 # Configuration template
.gitignore                   # Git untracked pattern configuration
README.md                    # Setup and usage guide
ARCHITECTURE.md              # Detailed design and routing structure
```

---

## Setup & Installation

### Prerequisite
Ensure you have **Python 3.11.0+** installed.

### 1. Create and Activate Virtual Environment
```bash
# From the project root
python -m venv .venv

# On Windows (PowerShell/CMD)
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file at the root of the project based on the template in `.env.example`:
```env
GEMINI_API_KEY=your_google_gemini_api_key
TAVILY_API_KEY=your_tavily_search_api_key
GEMINI_MODEL=gemini-1.5-flash
```

---

## Running and Testing the Agent

### Method A: Local Test Script (Recommended for Quick Verification)
Run the offline command-line test script to verify the ReAct loop directly:
```bash
# To run in interactive mode (it will prompt you for an objective):
python -m backend.test_agent

# To run with an inline custom prompt/objective:
python -m backend.test_agent "Find the latest research papers on multi-agent frameworks and identify key trends."
```
This runs the agent to solve the provided objective. You will see live trace step outputs (`REASONING_STATUS`, `ACTION`, `TOOL_RESULT`, etc.) and the final generated report.

### Method B: Running the FastAPI Web Server
1. Start the server using Uvicorn:
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Check the API health by opening [http://localhost:8000/api/health](http://localhost:8000/api/health) in your browser.

3. Trigger the agent via API:
   **Endpoint**: `POST /api/agent/run`  
   **Payload**:
   ```json
   {
     "objective": "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization.",
     "max_iterations": 8
   }
   ```
   **Example curl Command**:
   ```bash
   curl -X POST http://localhost:8000/api/agent/run \
     -H "Content-Type: application/json" \
     -d '{"objective": "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization."}'
   ```
