# Agent X — System Architecture & LangGraph Design

## Overview

Agent X implements a genuine ReAct (Reasoning and Action) loop using LangGraph. Rather than relying on a hardcoded pipeline, the agent continuously evaluates its state, collected evidence, and missing information to select the next action dynamically.

## LangGraph State Flow

```
[START]
   ↓
[REASON NODE]
   ↓
[CONDITIONAL ROUTER]
   ├── "web_search" ─────────► [WEB SEARCH NODE] ─────────┐
   ├── "research_search" ────► [RESEARCH SEARCH NODE] ────┤
   ├── "analyze_information" ► [ANALYZE NODE] ────────────┤
   └── "finish" ─────────────► [FINISH NODE] ───► [END]   │
                                    ▲                     │
                                    └─────────────────────┘
```

## Agent State Schema (`AgentState`)

- `objective` (str): User intelligence objective.
- `web_results` (list[dict]): Collected web search evidence.
- `research_results` (list[dict]): Collected arXiv research paper evidence.
- `analysis_results` (dict): Synthesized insights from Gemini analysis.
- `actions_taken` (list[str]): Log of tool execution steps.
- `iteration_count` (int): Number of ReAct graph loops executed.
- `max_iterations` (int): Hard safety limit (8).
- `task_complete` (bool): Completion flag.
- `final_report` (dict): Structured final intelligence report.
- `trace_events` (list[dict]): Safe, high-level trace logs for client display.
- `errors` (list[str]): Non-fatal warnings and error logs.

## Tool Capabilities

1. **`web_search`**: Tavily API integration targeting market news, product launches, competitor activity, and industry trends.
2. **`research_search`**: arXiv API REST integration parsing XML feeds for scientific publications, technical papers, and algorithmic advances.
3. **`analyze_information`**: Gemini LLM call synthesizing only empirical evidence collected from prior tool calls.
4. **`finish`**: Compiles final structured intelligence report adhering to all required report sections.

## Safety & Security Safeguards

- High-level `REASONING_STATUS` only; private chain-of-thought and internal prompt text are never exposed.
- API keys are managed exclusively via environment variables (`GEMINI_API_KEY`, `TAVILY_API_KEY`).
- Iteration limit enforced at 8 iterations to prevent infinite loops.
- Graceful degradation when network or API limits occur.
