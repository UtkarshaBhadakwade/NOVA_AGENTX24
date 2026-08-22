import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.tools import web_search, research_search, crossref_search, analyze_information

# Load environment variables
load_dotenv()

logger = logging.getLogger("agent_x.agent")

MAX_ITERATIONS = 8

def reasoning_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates current agent state, missing information, collected evidence, and previous actions.
    Decides the single next tool action or whether to complete the task.
    Emits safe reasoning status without exposing private chain-of-thought.
    """
    objective = state["objective"]
    web_results = state.get("web_results", [])
    research_results = state.get("research_results", [])
    crossref_results = state.get("crossref_results", [])
    analysis_results = state.get("analysis_results")
    actions_taken = state.get("actions_taken", [])
    iteration_count = state.get("iteration_count", 0) + 1

    new_trace_events = []
    new_errors = []

    # Check Max Iterations limit (8)
    if iteration_count >= MAX_ITERATIONS:
        logger.info("Maximum iteration limit (8) reached.")
        new_trace_events.append({
            "event": "[DECISION]",
            "detail": "Maximum iteration limit reached. Generating the best evidence-based report from available information."
        })
        if not analysis_results:
            next_action = "analyze_information"
            reasoning_status = "Maximum iteration limit reached. Executing final information analysis."
        else:
            next_action = "finish"
            reasoning_status = "Maximum iteration limit reached. Concluding intelligence gathering."
        
        new_trace_events.append({"event": "[REASONING_STATUS]", "detail": reasoning_status})
        return {
            "iteration_count": iteration_count,
            "actions_taken": [f"reasoning -> {next_action}"],
            "trace_events": new_trace_events,
            "next_action": next_action,
            "search_query": objective
        }

    # First event check
    if not state.get("trace_events"):
        new_trace_events.append({
            "event": "[AGENT START]",
            "detail": f"Objective: {objective}"
        })

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    # Call Gemini for dynamic decision if API key is present
    decision_json = None
    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import SystemMessage, HumanMessage

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.6-flash",
                google_api_key=api_key,
                temperature=0.1
            )

            prompt = f"""
You are the central decision node for NOVAagent, an autonomous competitive intelligence agent.

USER OBJECTIVE:
"{objective}"

CURRENT AGENT STATE:
- Iteration Count: {iteration_count}/{MAX_ITERATIONS}
- Actions Taken So Far: {actions_taken}
- Web Search Results Count (Tavily API): {len(web_results)}
- arXiv Research Results Count: {len(research_results)}
- CrossRef Research Results Count: {len(crossref_results)}
- Strategic Analysis Completed: {bool(analysis_results)}

EVIDENCE SUMMARY:
Web Results Titles (Tavily): {[r.get('title') for r in web_results]}
arXiv Results Titles: {[r.get('title') for r in research_results]}
CrossRef Results Titles: {[r.get('title') for r in crossref_results]}

INSTRUCTIONS:
Evaluate missing information needed for the objective. Select ONE next action:
1. "web_search": Need real-time web data, industry news, competitor launches, market developments via Tavily Search API.
2. "research_search": Need academic papers, scientific publications, patent/technical trends on arXiv.
3. "crossref_search": Need peer-reviewed research papers, DOIs, or publisher publications on CrossRef.
4. "analyze_information": Have collected raw web/research evidence; now need to synthesize into strategic insights.
5. "finish": Analysis is complete, and sufficient evidence has been gathered to produce the final intelligence report.

RULES FOR SELECTION:
- If web_search has NOT been run yet, pick "web_search".
- If research_search has NOT been run yet, pick "research_search".
- If crossref_search has NOT been run yet, pick "crossref_search".
- If evidence exists (or search tools were run) but analyze_information has NOT been run yet, pick "analyze_information".
- If analyze_information has been completed, pick "finish".

Output strictly valid JSON matching this schema:
{{
  "action": "web_search" | "research_search" | "crossref_search" | "analyze_information" | "finish",
  "reasoning_status": "<High-level 1-sentence safe status describing why this action is selected without private CoT>",
  "search_query": "<Focused query string for search action, or empty string if analyze/finish>"
}}
"""
            messages = [
                SystemMessage(content="You are a strategic intelligence agent routing node."),
                HumanMessage(content=prompt)
            ]

            res = llm.invoke(messages)
            raw_content = res.content
            if isinstance(raw_content, list):
                content_str = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in raw_content]).strip()
            else:
                content_str = str(raw_content).strip()

            if content_str.startswith("```json"):
                content_str = content_str[7:]
            if content_str.startswith("```"):
                content_str = content_str[3:]
            if content_str.endswith("```"):
                content_str = content_str[:-3]
            content_str = content_str.strip()

            decision_json = json.loads(content_str)
        except Exception as e:
            logger.error(f"Gemini reasoning node error: {str(e)}")
            new_errors.append(f"Reasoning LLM warning: {str(e)}")

    # Deterministic dynamic fallbacks if Gemini API is missing or encounters issues
    if not decision_json:
        web_called = any("web_search" in a for a in actions_taken)
        research_called = any("research_search" in a for a in actions_taken)
        crossref_called = any("crossref_search" in a for a in actions_taken)
        analyze_called = any("analyze_information" in a for a in actions_taken)

        if not web_called:
            decision_json = {
                "action": "web_search",
                "reasoning_status": "Current industry and competitor developments are needed via Tavily Web Search.",
                "search_query": objective
            }
        elif not research_called:
            decision_json = {
                "action": "research_search",
                "reasoning_status": "Need research paper evidence from arXiv to validate emerging technical trends.",
                "search_query": objective
            }
        elif not crossref_called:
            decision_json = {
                "action": "crossref_search",
                "reasoning_status": "Need research paper evidence from CrossRef to validate peer-reviewed publications.",
                "search_query": objective
            }
        elif not analyze_called:
            decision_json = {
                "action": "analyze_information",
                "reasoning_status": "Sufficient evidence collected; proceeding with strategic information analysis.",
                "search_query": ""
            }
        else:
            decision_json = {
                "action": "finish",
                "reasoning_status": "Competitive intelligence gathering and analysis completed.",
                "search_query": ""
            }

    action = decision_json.get("action", "finish")
    reasoning_status = decision_json.get("reasoning_status", "Evaluating next intelligence gathering action.")
    search_query = decision_json.get("search_query", objective) or objective

    # Validate action
    valid_actions = ["web_search", "research_search", "crossref_search", "analyze_information", "finish"]
    if action not in valid_actions:
        new_errors.append(f"Invalid action '{action}' returned by reasoning node. Defaulting safely.")
        action = "finish"

    new_trace_events.append({
        "event": "[REASONING_STATUS]",
        "detail": reasoning_status
    })

    return {
        "iteration_count": iteration_count,
        "actions_taken": [f"reasoning -> {action}"],
        "trace_events": new_trace_events,
        "errors": new_errors,
        "next_action": action,
        "search_query": search_query
    }


def web_search_node(state: AgentState) -> Dict[str, Any]:
    query = state.get("search_query", state["objective"])
    
    results = web_search(query)
    
    new_trace_events = [
        {
            "event": "[ACTION]",
            "detail": f"Tool: web_search (Tavily Search API) | Query: '{query}'"
        },
        {
            "event": "[TOOL_RESULT]",
            "detail": f"web_search (Tavily Web Search) returned {len(results)} structured results."
        }
    ]
    
    return {
        "web_results": results,
        "actions_taken": [f"web_search (query: {query})"],
        "trace_events": new_trace_events
    }


def research_search_node(state: AgentState) -> Dict[str, Any]:
    query = state.get("search_query", state["objective"])
    
    results = research_search(query)
    
    new_trace_events = [
        {
            "event": "[ACTION]",
            "detail": f"Tool: research_search (arXiv REST API) | Query: '{query}'"
        },
        {
            "event": "[TOOL_RESULT]",
            "detail": f"research_search returned {len(results)} arXiv papers."
        }
    ]
    
    return {
        "research_results": results,
        "actions_taken": [f"research_search (query: {query})"],
        "trace_events": new_trace_events
    }


def crossref_search_node(state: AgentState) -> Dict[str, Any]:
    query = state.get("search_query", state["objective"])
    
    results = crossref_search(query)
    
    new_trace_events = [
        {
            "event": "[ACTION]",
            "detail": f"Tool: crossref_search (CrossRef REST API) | Query: '{query}'"
        },
        {
            "event": "[TOOL_RESULT]",
            "detail": f"crossref_search returned {len(results)} CrossRef papers."
        }
    ]
    
    return {
        "crossref_results": results,
        "actions_taken": [f"crossref_search (query: {query})"],
        "trace_events": new_trace_events
    }


def analyze_node(state: AgentState) -> Dict[str, Any]:
    objective = state["objective"]
    web_results = state.get("web_results", [])
    research_results = state.get("research_results", [])
    crossref_results = state.get("crossref_results", [])

    analysis = analyze_information(objective, web_results, research_results, crossref_results)

    new_trace_events = [
        {
            "event": "[ACTION]",
            "detail": "Tool: analyze_information (Gemini 3.6 Flash) | Synthesizing Tavily web, arXiv, and CrossRef evidence."
        },
        {
            "event": "[TOOL_RESULT]",
            "detail": f"Strategic analysis complete with confidence level: {analysis.get('confidence_level', 'N/A')}."
        }
    ]

    return {
        "analysis_results": analysis,
        "actions_taken": ["analyze_information"],
        "trace_events": new_trace_events
    }


def finish_node(state: AgentState) -> Dict[str, Any]:
    objective = state["objective"]
    web_results = state.get("web_results", [])
    research_results = state.get("research_results", [])
    crossref_results = state.get("crossref_results", [])
    analysis = state.get("analysis_results") or {}

    # Compile Sources Used
    sources_used = []
    for item in web_results:
        if item.get("url"):
            sources_used.append(f"Web (Tavily): {item.get('title')} ({item.get('url')})")
    for item in research_results:
        if item.get("url"):
            sources_used.append(f"arXiv: {item.get('title')} ({item.get('url')})")
    for item in crossref_results:
        if item.get("url"):
            sources_used.append(f"CrossRef: {item.get('title')} ({item.get('url')})")

    # Important evidence summary
    important_evidence = []
    for item in web_results[:2]:
        important_evidence.append(f"Web Evidence (Tavily): {item.get('title')} - {item.get('content')[:150]}...")
    for item in research_results[:2]:
        important_evidence.append(f"Research Paper (arXiv): {item.get('title')} - {item.get('summary')[:150]}...")
    for item in crossref_results[:2]:
        important_evidence.append(f"Research Paper (CrossRef): {item.get('title')} - {item.get('summary')[:150]}...")

    final_report = {
        "EXECUTIVE SUMMARY": f"Competitive intelligence assessment regarding '{objective}'. Analyzed {len(web_results)} web sources via Tavily API, {len(research_results)} arXiv research papers, and {len(crossref_results)} CrossRef research papers.",
        "KEY DEVELOPMENTS": analysis.get("key_developments", ["Active developments observed in market and research data."]),
        "IMPORTANT EVIDENCE": important_evidence if important_evidence else ["Collected empirical data from Tavily web search, arXiv, and CrossRef."],
        "EMERGING TRENDS": analysis.get("emerging_trends", ["Accelerated momentum in key technological capabilities."]),
        "OPPORTUNITIES": analysis.get("opportunities", ["Strategic expansion into identified high-impact sectors."]),
        "THREATS AND RISKS": analysis.get("threats_and_risks", ["Potential market displacement and technological disruption."]),
        "STRATEGIC IMPLICATIONS": analysis.get("strategic_implications", ["Organisations should maintain proactive monitoring and agile response capability."]),
        "RECOMMENDED ACTIONS": analysis.get("recommended_actions", ["Implement regular intelligence updates and evaluate strategic pilot initiatives."]),
        "CONFIDENCE LEVEL": analysis.get("confidence_level", "HIGH"),
        "SOURCES USED": sources_used if sources_used else ["Tavily Web, arXiv, and CrossRef research feeds"]
    }

    new_trace_events = [
        {
            "event": "[DECISION]",
            "detail": "Sufficient evidence collected and analyzed. Generating final intelligence report."
        },
        {
            "event": "[TASK_COMPLETE]",
            "detail": "Task execution finished successfully."
        },
        {
            "event": "[FINAL INTELLIGENCE REPORT]",
            "detail": final_report
        }
    ]

    return {
        "task_complete": True,
        "final_report": final_report,
        "actions_taken": ["finish"],
        "trace_events": new_trace_events
    }


def route_next_action(state: AgentState) -> str:
    """
    Conditional router mapping decision to graph edges.
    """
    return state.get("next_action", "finish")


# Construct LangGraph State Graph
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("reason", reasoning_node)
graph_builder.add_node("web_search", web_search_node)
graph_builder.add_node("research_search", research_search_node)
graph_builder.add_node("crossref_search", crossref_search_node)
graph_builder.add_node("analyze_information", analyze_node)
graph_builder.add_node("finish", finish_node)

# Set entry point
graph_builder.set_entry_point("reason")

# Conditional edges from reason node
graph_builder.add_conditional_edges(
    "reason",
    route_next_action,
    {
        "web_search": "web_search",
        "research_search": "research_search",
        "crossref_search": "crossref_search",
        "analyze_information": "analyze_information",
        "finish": "finish"
    }
)

# Connect tool execution back to reason node (ReAct loop)
graph_builder.add_edge("web_search", "reason")
graph_builder.add_edge("research_search", "reason")
graph_builder.add_edge("crossref_search", "reason")
graph_builder.add_edge("analyze_information", "reason")

# Connect finish to END
graph_builder.add_edge("finish", END)

# Compile agent graph
agent_graph = graph_builder.compile()
