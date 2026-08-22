# NOVA Agent — Autonomous Competitive Intelligence System

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Deployed-success?style=flat-square&logo=vercel)](https://nova-agentx-24.vercel.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)

---

## 👥 Team Members

- **Utkarsha Bhadakwade**
- **Pranav Gaikwad**
- **Vedika Pangavhane**
- **Shriraj Kamble**
- **Prathamesh Kolhe**

---

## 🎯 Problem Statement

Organizations, startups, and research institutions operate in highly competitive environments where staying updated on scientific research, patent developments, competitor product launches, and industry trends is critical. However, manually monitoring scientific publications, patent databases, web news, and industry reports is time-consuming, inefficient, and prone to missing critical updates.

**NOVA Agent** solves this by orchestrating autonomous multi-agent networks that continuously track research and market activities, analyze multi-source data, and deliver structured, evidence-grounded strategic intelligence reports in real time.

---

## 🚀 Project Overview & Architecture

**NOVA Agent** is an Autonomous Competitive Intelligence Platform engineered to transform fragmented market and academic data into structured strategic intelligence. Built on a **ReAct (Reasoning + Action) multi-agent architecture using LangGraph**, NOVA Agent dynamically delegates tasks across specialized agents, collects evidence, evaluates findings, and generates structured executive reports.

### 🤖 Specialized Multi-Agent Network

| Agent Name | Role | Responsibilities & Tools |
| :--- | :--- | :--- |
| **Supervisor Agent** | Task Orchestrator & Delegator | Inspects state, evaluates information gaps, and dynamically delegates next tasks without hardcoded sequences. Enforces safety guardrails. |
| **Research Agent** | Scientific & Technical Specialist | Queries **arXiv REST API** and **CrossRef REST API** for scientific papers, DOIs, technical developments, and publication year metadata. |
| **Market Intelligence Agent** | Competitor & Industry Specialist | Queries **Tavily Web Search API** for live web news, competitor product launches, company activities, and market developments. |
| **Strategic Synthesis Agent** | Strategic Intelligence Analyst | Synthesizes multi-source evidence using **Google Gemini 3.6 Flash** into structured, grounded intelligence reports without inventing unsupported facts. |

---

## 📊 Application Architecture & Flow Diagram

```
                             USER OBJECTIVE
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │       SUPERVISOR AGENT       │◄──────────────────────────┐
                    │ (Evaluates Gaps & Delegates) │                           │
                    └──────────────┬───────────────┘                           │
                                   │ Dynamic Delegation                        │
             ┌─────────────────────┼─────────────────────┐                     │
             ▼                     ▼                     ▼                     │
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
    │  RESEARCH AGENT  │  │  MARKET AGENT    │  │ SYNTHESIS AGENT  │           │
    │ (arXiv / CrossRef│  │  (Tavily Web)    │  │ (Gemini 3.6 Flash│           │
    └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘           │
             │                     │                     │                     │
             └─────────────────────┴─────────────────────┴─────────────────────┘
                                           │
                                           ▼
                                 Updates Shared State
                                   & Enforces Limits
```

---

## ✨ Key Features & Improvements

### 1. 🗂️ Persistent Investigation History Sidebar
- **Workspace Navigation**: Includes `+ New Investigation`, live history search, and organized `PINNED` and `RECENT` investigation sections.
- **SQLite Database Persistence**: Automatically saves finished investigations to SQLite (`investigations.db` locally or `/tmp/investigations.db` on Vercel).
- **One-Click Recall**: Clicking any previous investigation instantly reloads its saved report, execution logs, and selected filters.
- **Non-Fatal Memory Isolation**: Long-term memory storage errors log safe warnings and never crash the main agent execution.

### 2. 📅 Timeline & Publication Year Filters
- **Timeline Filtering**: Filter research by `Latest`, `Last 30 Days`, `Last 3 Months`, `Last 6 Months`, or `Last 1 Year`.
- **Publication Year Filtering**: Prioritize papers by specific years (`Any Year`, `2026`, `2025`, `2024`, `2023`, `Earlier`).

### 3. 🎓 Research Source & Journal Quartile Filters
- **Source Selection**: Filter between `All Sources`, `arXiv Papers`, `CrossRef Publications`, `Journal Articles`, or `Conference Papers`.
- **Journal Quartiles (Q1, Q2, Q3, Q4)**: Automatic classification and filtering of academic papers into Q1 (High Impact), Q2 (Mid-High Impact), Q3, and Q4 journal quartiles based on publisher prestige, venues, and citation counts.

### 4. ⚡ Simplified Agent Execution Timeline
- Displays clean **Process & Orchestration** details (`Supervisor Agent`, `Research Agent`, `Market Intelligence Agent`, `Strategic Synthesis Agent`).
- Eliminates duplicated tool result cards, keeping the execution pane minimal and focused on orchestration.

### 5. 📑 Redesigned 9-Part Final Intelligence Report
Structured, evidence-grounded intelligence dashboard containing:
1. **Executive Summary**: Strategic overview, main finding, and confidence level.
2. **Key Developments**: Categorized cards (`Research`, `Market`, `Competitor`, `Technology`).
3. **Emerging Trends**: Industry and technical trends list.
4. **Strategic Opportunities**: Opportunity title, why it matters, and potential impact.
5. **Threats and Risks**: Priority risk cards (`High Risk`, `Medium Risk`, `Low Risk`).
6. **Strategic Implications**: Organizational guidance for investment and monitoring.
7. **Recommended Actions**: Prioritized recommendations (`Priority 1: Immediate`, `Priority 2: Short-Term`, `Priority 3: Long-Term`).
8. **Dedicated Evidence & Sources**: Clickable source cards with Quartile & Source badges (`Web`, `arXiv`, `CrossRef`).
9. **Confidence & Coverage Summary**: Metrics showing confidence level, evidence item counts, and selected timeline context.

### 6. 🚫 Clean Professional UI (No Emojis)
- Professional typography, Lucide-inspired SVG icon set, crisp borders, and minimalist warm off-white palette.

---

## 🛠️ Technology Stack

- **Agent Orchestration**: Python 3.11+, LangGraph, LangChain Core
- **LLM Reasoning & Synthesis**: Google Gemini 3.6 Flash (`langchain-google-genai`)
- **Search & Tool APIs**:
  - **Tavily Web Search API**: Live web market news and competitor developments
  - **arXiv REST XML API**: Scientific publications and technical preprints
  - **CrossRef REST API**: Peer-reviewed journals, DOIs, and conference proceedings
- **Persistence & Backend**: FastAPI, Uvicorn, SQLite3, Pydantic v2, Python-Dotenv
- **Web Frontend**: HTML5, Vanilla CSS3, Vanilla JavaScript (Single-Page Workspace)
- **Serverless Hosting**: Vercel Serverless (`@vercel/python` with 60s `maxDuration`)

---

## 🚀 Live Demo & Deployment Guide

### Live Application Link:
👉 **[https://nova-agentx-24.vercel.app](https://nova-agentx-24.vercel.app)**

### Vercel Deployment Steps:
1. Import repository `https://github.com/UtkarshaBhadakwade/NOVA_AGENTX24` on [Vercel](https://vercel.com/new).
2. Configure Environment Variables under **Project Settings ➔ Environment Variables**:
   - `GEMINI_API_KEY` = your Google Gemini API key
   - `TAVILY_API_KEY` = your Tavily Search API key
3. Click **Deploy**!

---

## 💻 Local Installation & Setup

### 1. Clone Directory & Navigate
```powershell
cd "c:\Users\VEDIKA\Downloads\New folder"
```

### 2. Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file inside `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## ⚙️ Running Locally

### Option A: Terminal Verification Test Suite
Run the 3-scenario Task 3 verification suite:
```powershell
.\venv\Scripts\python backend/test_agent.py
```

### Option B: Start FastAPI Web Server & UI
Launch the server and access the interactive Web Dashboard:
```powershell
.\venv\Scripts\uvicorn backend.main:app --reload --port 8000
```
Open your browser and visit:
👉 **`http://localhost:8000`**

---

## 📸 Interface Screenshots

### 1. NOVA Agent Workspace & Investigation History Sidebar
![NOVA Agent Workspace](docs/screenshots/dashboard_welcome.png)

### 2. Redesigned 9-Part Final Intelligence Report Output
![NOVA Agent Intelligence Report](docs/screenshots/dashboard_results.png)
