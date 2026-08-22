# NOVA Agent — Generated System Documentation

This document summarizes the complete architectural, algorithmic, and interface design of the **NOVA Agent Autonomous Competitive Intelligence System**.

## 1. System Overview
NOVA Agent is built on **LangGraph**, **FastAPI**, **Google Gemini 3.6 Flash**, **Tavily**, **arXiv**, and **CrossRef**. It operates an autonomous loop that plans, searches, cross-verifies, evaluates hypotheses, resolves evidence conflicts, and synthesizes 11-part grounded intelligence reports.

## 2. Multi-Agent Network Roles
- **Supervisor Agent**: Dynamic Task Orchestrator (`[PLANNING]`, `[PLAN_CREATED]`, `[PARALLEL_EXECUTION]`).
- **Research Agent**: Academic specialist querying arXiv REST XML API and CrossRef REST API.
- **Market Intelligence Agent**: Web specialist querying Tavily Search API.
- **Evaluator Agent**: Quality assurance node performing self-evaluation (`[SELF_EVALUATION]`), testing hypotheses (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `INSUFFICIENT_EVIDENCE`), and detecting conflicts (`[CONFLICT_DETECTED]`).
- **Strategic Synthesis Agent**: Generates structured 11-part intelligence dashboards.

## 3. Persistent Memory System
- **Short-Term Memory**: LangGraph shared state dictionary (`AgentState`) maintained across graph nodes.
- **Long-Term Memory**: SQLite database (`investigations.db` / `/tmp/investigations.db`) saving full investigation objects and trace logs.
