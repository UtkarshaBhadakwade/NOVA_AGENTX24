# NOVAagent — Autonomous Competitive Intelligence Agent

## Team Members
- **Utkarsha Bhadakwade**
- **Pranav Gaikwad**
- **Vedika Pangavhane**

---

## Problem Statement

Organizations, startups, and research institutions operate in highly competitive and rapidly evolving environments where staying updated on research trends, patent developments, competitor strategies, and industry news is critical. However, manually monitoring scientific publications, patent databases, news platforms, and social media sources is time-consuming, inefficient, and prone to missing important updates. The lack of timely insights can result in lost opportunities, delayed innovation, and weakened competitive positioning. Therefore, there is a need for an autonomous AI agent capable of continuously tracking research and competitor activities, analyzing vast information sources, and delivering concise, actionable insights in real time.

---

## Project Description

**NOVAagent** is an Autonomous Competitive Intelligence Agent engineered to transform raw, fragmented market and academic data into structured, actionable strategic intelligence. Built on a genuine **ReAct (Reasoning + Action) state graph architecture using LangGraph**, NOVAagent continuously evaluates intelligence objectives, identifies missing information, dynamically selects specialized search and synthesis tools, and iteratively updates its internal state.

---

## Application Architecture & Workflow Flow

```
USER OBJECTIVE ──► REASONING NODE ──► ROUTER ──► DYNAMIC TOOLS ──► STATE UPDATE ──► REPORT
```

1. **User Objective**: Submitted via Web UI or REST API (`POST /analyze`).
2. **Reasoning Node**: Analyzes objective and missing information.
3. **Dynamic Tools**: Chooses `web_search` (Tavily), `research_search` (arXiv), `analyze_information` (Gemini 3.6 Flash), or `finish`.
4. **State Persistence**: LangGraph updates `AgentState` via list reducers.
5. **Interactive Report**: Formats report with executive summary, developments, opportunities, threats, and grounded sources.

---

## Technologies Used

- **Core Reasoning & Agent Graph**: Python 3.11+, LangGraph, LangChain Core
- **LLM Synthesis & Reasoning**: Google Gemini API (`gemini-3.6-flash`)
- **Search & Tool APIs**: Tavily Web Search API & arXiv REST XML API
- **Backend Framework**: FastAPI, Uvicorn, Pydantic v2
- **Web Frontend**: HTML5, Vanilla CSS3 (Beige/Off-White UI), Vanilla JavaScript

---

## How to Run the Project

### Terminal Test Execution
```powershell
.\venv\Scripts\python backend/test_agent.py
```

### Live Web Application & Dashboard
```powershell
.\venv\Scripts\uvicorn backend.main:app --reload --port 8000
```
Open **`http://localhost:8000`** in your browser.
