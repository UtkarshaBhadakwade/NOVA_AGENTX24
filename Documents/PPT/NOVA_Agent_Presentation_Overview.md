# NOVA Agent — Presentation Slide Outline (PPT)

## Slide 1: Title & Team
- **Title**: NOVA Agent — Autonomous Competitive Intelligence System
- **Team**: Utkarsha Bhadakwade, Pranav Gaikwad, Vedika Pangavhane, Shriraj Kamble, Prathamesh Kolhe
- **Deployment**: https://nova-agentx-24.vercel.app

## Slide 2: Problem Statement & Vision
- Enterprise competitive intelligence is fragmented across web news, academic papers, and market reports.
- Manual synthesis is slow, incomplete, and misses critical competitive moves.
- **Vision**: An autonomous multi-agent platform that gathers, cross-verifies, evaluates hypotheses, and synthesizes 11-part grounded reports in real time.

## Slide 3: Architecture & Multi-Agent Network
- **LangGraph Core**: Cyclic state graph with checkpointer (`MemorySaver`).
- **Supervisor Agent**: Dynamic planning & parallel dispatch.
- **Research Agent**: arXiv & CrossRef scientific literature tools.
- **Market Intelligence Agent**: Tavily live web search API.
- **Evaluator Agent**: Self-evaluation, conflict detection & hypothesis verification.
- **Strategic Synthesis Agent**: Google Gemini 3.6 Flash analyst.

## Slide 4: Key Capabilities & Features
- Persistent Investigation History & Visible History Search.
- Short-Term & Long-Term Memory Visualization Badges.
- Tool Fallbacks & Loop/Deadlock Recovery.
- 11-Part Intelligence Dashboard with Journal Quartiles (Q1, Q2, Q3, Q4).

## Slide 5: Live Demo & Impact
- Zero-downtime serverless deployment on Vercel (`api/index.py`).
- Instant competitive intelligence generation in under 10 seconds.
