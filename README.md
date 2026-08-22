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

Unlike traditional single-turn chatbots or hardcoded pipelines, NOVAagent makes real-time decisions:
1. **Evaluates Objective & State**: Determines whether real-time industry news, competitor activity, or scientific publications are required.
2. **Executes Autonomous Tools**: Gathers real live web data via Tavily API and academic research publications via arXiv API.
3. **Synthesizes Strategic Evidence**: Leverages Google Gemini 3.6 Flash to analyze collected findings without inventing unsupported facts.
4. **Generates Executive Reports**: Renders actionable competitive intelligence reports categorized into Executive Summaries, Key Developments, Emerging Trends, Strategic Opportunities, Threats & Risks, Implications, Recommended Actions, and Grounded Source References.

---

## Hackathon Evaluation & Judging Criteria Coverage

| Criteria | What Judges Check | How NOVAagent Fulfills It |
| :--- | :--- | :--- |
| **Problem Understanding** | Does the solution actually solve the given problem? | **YES.** Continuously tracks scientific papers (arXiv) and market news (Tavily), delivering structured intelligence reports to prevent missed updates. |
| **Agentic Behavior** | Does the AI reason, plan and act? | **YES.** Built on a genuine LangGraph ReAct loop (`START` → `REASON` → `ROUTER` → `TOOL` → `REASON` → `FINISH`) that dynamically plans and acts. |
| **Tool Usage** | Does the agent use tools effectively? | **YES.** Uses specialized autonomous tools (`web_search`, `research_search`, `analyze_information`) based on missing info. |
| **Autonomy** | Can it perform multi-step tasks? | **YES.** Operates completely autonomously over multi-iteration loops (e.g. Iteration 1 to 4) without human intervention. |
| **Adaptability** | Can it handle changing situations? | **YES.** Dynamic tool selection routes differently for competitor queries (`web_search`), research queries (`research_search`), or broad intelligence tasks. |
| **Error Handling** | Can it recover from failures? | **YES.** Handles missing keys, empty results, API timeouts, invalid tool choices, and enforces an 8-iteration safety guardrail. |
| **Innovation** | Is the solution creative/useful? | **YES.** Combines real-time web market evidence with peer-reviewed arXiv papers into a unified, actionable intelligence workspace. |
| **Accuracy** | Are the results reliable? | **YES.** Synthesizes findings strictly grounded in retrieved evidence, with clickable web URLs and arXiv PDF citations. |
| **User Experience** | Is the bot easy to use? | **YES.** Features a sleek, non-scrollable beige/off-white Web Dashboard (`http://localhost:8000`) with sample prompts and a live ReAct execution stream. |
| **Deployment** | Is the solution actually deployed and working? | **YES.** Deployed as a live FastAPI service (`POST /analyze`, `GET /`) with real end-to-end execution verified. |

---

## Technologies Used

- **Core Reasoning & Agent Graph**: Python 3.11+, LangGraph, LangChain Core
- **LLM Synthesis & Reasoning**: Google Gemini API (`gemini-3.6-flash` via `langchain-google-genai`)
- **Search & Tool APIs**:
  - **Tavily Web Search API**: Real-time competitor news, product launches, and industry trends
  - **arXiv REST XML API**: Academic papers, technical trends, and scientific publications
- **Backend Framework**: FastAPI, Uvicorn, Pydantic v2, Python-Dotenv
- **Web Frontend**: HTML5, Vanilla CSS3 (Minimal Off-White / Warm Beige Design), Vanilla JavaScript

---

## Features

- 🧠 **Genuine ReAct State Loop**: Dynamic graph loop (`START` → `REASON` → `CONDITIONAL ROUTER` → `TOOLS` → `REASON` → `FINISH`) enforcing real reasoning over hardcoded chains.
- 🛠️ **Dynamic Autonomous Tool Selection**: Dynamically routes between `web_search`, `research_search`, `analyze_information`, and `finish`.
- 📊 **Structured Intelligence Dashboard**: Categorizes insights into Executive Summary, Key Developments, Emerging Trends, Strategic Opportunities, Threats & Risks, Strategic Implications, and Recommended Actions.
- 🔗 **Grounded Sources & Citations**: Direct clickable links to live web articles and arXiv paper PDFs.
- 🛡️ **Safe Trace Event Logging**: Exposes safe, high-level trace events (`[REASONING_STATUS]`, `[ACTION]`, `[TOOL_RESULT]`, `[DECISION]`) without exposing private chain-of-thought, internal prompts, or API keys.
- ⚡ **Iteration Guardrails & Error Safety**: Enforces a safety maximum limit of 8 iterations and handles API failures gracefully.
- 🎨 **Minimalist Non-Scrollable UI**: Clean off-white and warm beige dashboard (`100vh`) with fixed viewport layout and internal pane scrolling.

---

## Installation / Setup Steps

### 1. Clone or Open Project Directory
```powershell
cd "c:\Users\VEDIKA\Downloads\New folder"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file inside `backend/.env` (or root `.env`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## How to Run the Project

### Option A: Run the End-to-End Terminal Verification
To execute the ReAct agent graph test directly in your terminal:
```powershell
.\venv\Scripts\python backend/test_agent.py
```

### Option B: Start the Web Application & Server
To launch the live FastAPI web server and access the Web Dashboard:
```powershell
.\venv\Scripts\uvicorn backend.main:app --reload --port 8000
```
Open your browser and visit:
👉 **`http://localhost:8000`**

---

## Screenshots / Demo

### 1. NOVAagent Intelligence Workspace (Initial View)
![NOVAagent Workspace](docs/screenshots/dashboard_welcome.png)

### 2. Live Agent Execution & Competitive Intelligence Report Output
![NOVAagent Intelligence Report](docs/screenshots/dashboard_results.png)
