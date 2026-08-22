import os
import json
from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from backend.state import AgentState
from backend.tools.arxiv import search_arxiv
from backend.tools.crossref import lookup_crossref
from backend.tools.analyze import analyze_information

# Define the structured decision schema for tools
class ToolSelection(BaseModel):
    selected: bool = Field(description="Whether to select and invoke this tool in this step.")
    reason: str = Field(description="Short, user-friendly explanation of why this tool was selected or skipped (e.g. 'Selected because the user requested recent AI research' or 'Skipped because DOI verification was not requested').")
    query: Optional[str] = Field(default=None, description="Search query or DOI input if selected.")

class AgentDecision(BaseModel):
    reasoning_status: str = Field(
        description="A high-level, user-friendly description of what you are doing next and why. Do NOT expose detailed chain-of-thought, keep it safe and summary-oriented."
    )
    arxiv: ToolSelection = Field(description="Decision and parameters for arXiv search.")
    crossref: ToolSelection = Field(description="Decision and parameters for Crossref lookup.")
    finish: bool = Field(
        description="Set to true if you have gathered and analyzed sufficient information to satisfy the objective, or if the objective requires no tool research."
    )

# Prompt template for the core agent reasoning
REASONING_SYSTEM_PROMPT = """You are an autonomous Competitive Intelligence Research Agent.

You have two tools: search_arxiv and lookup_crossref.

Dynamically select the minimum tools required for the user's request.
Never call tools unnecessarily.
You may call multiple tools when required.
After receiving a result, decide whether another tool is needed.
Never fabricate papers, authors, DOIs, publishers or research facts.
Base research claims on retrieved sources.
Return concise explanations of why a tool was selected or skipped.
Do not expose hidden chain-of-thought.

Below is the current state of your investigation:
- Iteration: {iterations}/{max_iterations}

Collected Evidence so far:
{evidence}

Structured Analysis Result (if any):
{analysis}

Previous Trace Steps:
{history}

Your task:
1. Evaluate what information is missing to satisfy the user's objective: {objective}
2. Determine which tool is appropriate, explain your decision, and select tools accordingly.
3. If no more research is needed, set finish=true.
"""

def normalize_title(title: str) -> str:
    if not title:
        return ""
    return "".join(c.lower() for c in title if c.isalnum())

def add_to_evidence(evidence: List[Dict[str, Any]], new_items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], int]:
    added_count = 0
    for item in new_items:
        found = False
        item_doi = item.get("doi", "").strip().lower() if item.get("doi") else ""
        item_arxiv_id = item.get("arxiv_id", "").strip().lower() if item.get("arxiv_id") else ""
        item_norm_title = normalize_title(item.get("title", ""))
        
        for existing in evidence:
            ext_doi = existing.get("doi", "").strip().lower() if existing.get("doi") else ""
            ext_arxiv_id = existing.get("arxiv_id", "").strip().lower() if existing.get("arxiv_id") else ""
            ext_norm_title = normalize_title(existing.get("title", ""))
            
            # Match condition
            match = False
            if item_doi and ext_doi and item_doi == ext_doi:
                match = True
            elif item_arxiv_id and ext_arxiv_id and item_arxiv_id == ext_arxiv_id:
                match = True
            elif item_norm_title and ext_norm_title and item_norm_title == ext_norm_title:
                match = True
                
            if match:
                # Merge fields
                if not existing.get("doi") and item.get("doi"):
                    existing["doi"] = item["doi"]
                if not existing.get("arxiv_id") and item.get("arxiv_id"):
                    existing["arxiv_id"] = item["arxiv_id"]
                if not existing.get("pdf_url") and item.get("pdf_url"):
                    existing["pdf_url"] = item["pdf_url"]
                if not existing.get("abstract") and item.get("abstract"):
                    existing["abstract"] = item["abstract"]
                if not existing.get("journal") and item.get("journal"):
                    existing["journal"] = item["journal"]
                if not existing.get("conference") and item.get("conference"):
                    existing["conference"] = item["conference"]
                if not existing.get("publisher") and item.get("publisher"):
                    existing["publisher"] = item["publisher"]
                if not existing.get("url") and item.get("url"):
                    existing["url"] = item["url"]
                
                # Merge sources
                existing_sources = set(existing.get("source", "").split(" & "))
                item_sources = set(item.get("source", "").split(" & "))
                existing["source"] = " & ".join(sorted(existing_sources.union(item_sources)))
                
                found = True
                break
        if not found:
            evidence.append(item)
            added_count += 1
    return evidence, added_count

def reasoning_node(state: AgentState) -> Dict[str, Any]:
    """
    Core reasoning node. Decides the next action using Gemini.
    """
    iterations = state.get("iterations", 0) + 1
    max_iterations = state.get("max_iterations", 8)
    
    if iterations > max_iterations:
        return {
            "iterations": iterations,
            "next_action": "finish",
            "next_action_input": None,
            "steps": state.get("steps", []) + [
                {
                    "type": "DECISION",
                    "content": "Maximum iteration limit reached. Automatically routing to compile final report."
                }
            ]
        }
    
    objective = state.get("objective", "")
    
    evidence_list = []
    for idx, ev in enumerate(state.get("collected_evidence", [])):
        source = ev.get("source", "Unknown")
        title = ev.get("title", "No Title")
        if "arXiv" in source:
            evidence_list.append(
                f"[{idx+1}] Source: arXiv | Title: {title} | ID: {ev.get('arxiv_id')}\nAbstract: {ev.get('abstract', '')[:200]}..."
            )
        else:
            evidence_list.append(
                f"[{idx+1}] Source: Crossref | Title: {title} | DOI: {ev.get('doi')}\nPublisher/Journal: {ev.get('publisher', '')}/{ev.get('journal', '')}"
            )
    evidence_str = "\n\n".join(evidence_list) if evidence_list else "No evidence collected yet."
    
    analysis_str = "None"
    if state.get("analysis_result"):
        analysis_str = json.dumps(state["analysis_result"], indent=2)
        
    history_list = []
    for step in state.get("steps", []):
        if step.get("type") == "REASONING_STATUS":
            history_list.append(f"[Reasoning] {step.get('content')}")
        elif step.get("type") == "ACTION":
            history_list.append(f"[Action] {step.get('content')}")
        elif step.get("type") == "TOOL_RESULT":
            history_list.append(f"[Result] {step.get('content')}")
        elif step.get("type") == "DECISION":
            history_list.append(f"[Decision] {step.get('content')}")
    history_str = "\n".join(history_list) if history_list else "No history yet."
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "iterations": iterations,
            "next_action": "finish",
            "error": "GEMINI_API_KEY is not set in the environment.",
            "steps": state.get("steps", []) + [
                {
                    "type": "DECISION",
                    "content": "Error: GEMINI_API_KEY is missing. Halting execution."
                }
            ]
        }
        
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1
        )
        structured_llm = llm.with_structured_output(AgentDecision)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", REASONING_SYSTEM_PROMPT),
            ("user", "What is the next step to address the objective?")
        ])
        
        chain = prompt | structured_llm
        decision = chain.invoke({
            "objective": objective,
            "iterations": iterations,
            "max_iterations": max_iterations,
            "evidence": evidence_str,
            "analysis": analysis_str,
            "history": history_str
        })
        
        new_steps = list(state.get("steps", []))
        
        # Log tool decisions for UI display
        new_steps.append({
            "type": "TOOL_DECISION",
            "content": {
                "arxiv": {
                    "selected": decision.arxiv.selected,
                    "reason": decision.arxiv.reason,
                    "query": decision.arxiv.query
                },
                "crossref": {
                    "selected": decision.crossref.selected,
                    "reason": decision.crossref.reason,
                    "query": decision.crossref.query
                }
            }
        })
        
        # Log reasoning status
        new_steps.append({
            "type": "REASONING_STATUS",
            "content": decision.reasoning_status
        })
        
        # Prioritize next tool to invoke sequentially
        next_action = "finish"
        next_action_input = None
        
        if not decision.finish:
            if decision.arxiv.selected:
                next_action = "search_arxiv"
                next_action_input = decision.arxiv.query
            elif decision.crossref.selected:
                next_action = "lookup_crossref"
                next_action_input = decision.crossref.query
        
        new_steps.append({
            "type": "DECISION",
            "content": f"Selected action: {next_action}" + (f" with query: '{next_action_input}'" if next_action_input else "")
        })
        
        return {
            "iterations": iterations,
            "next_action": next_action,
            "next_action_input": next_action_input,
            "steps": new_steps
        }
        
    except Exception as e:
        return {
            "iterations": iterations,
            "next_action": "finish",
            "error": f"Reasoning engine failed: {str(e)}",
            "steps": state.get("steps", []) + [
                {
                    "type": "DECISION",
                    "content": f"Reasoning failed due to error: {str(e)}. Stopping loop."
                }
            ]
        }

def arxiv_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes search_arxiv tool.
    """
    query = state.get("next_action_input", "")
    new_steps = list(state.get("steps", []))
    
    new_steps.append({
        "type": "ACTION",
        "content": f"search_arxiv(query='{query}')"
    })
    
    if not query:
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": "Empty arXiv search query. No papers retrieved."
        })
        return {"steps": new_steps, "next_action": None, "next_action_input": None}
        
    try:
        results = search_arxiv(query=query)
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Retrieved {len(results)} papers from arXiv."
        })
        
        current_evidence = list(state.get("collected_evidence", []))
        current_evidence, added_count = add_to_evidence(current_evidence, results)
        
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Added {added_count} new papers (deduplicated)."
        })
            
        return {
            "collected_evidence": current_evidence,
            "steps": new_steps,
            "next_action": None,
            "next_action_input": None
        }
    except Exception as e:
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"arXiv search failed: {str(e)}"
        })
        return {"steps": new_steps, "next_action": None, "next_action_input": None}

def crossref_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes lookup_crossref tool.
    """
    query = state.get("next_action_input", "")
    new_steps = list(state.get("steps", []))
    
    new_steps.append({
        "type": "ACTION",
        "content": f"lookup_crossref(query='{query}')"
    })
    
    if not query:
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": "Empty Crossref query. No metadata retrieved."
        })
        return {"steps": new_steps, "next_action": None, "next_action_input": None}
        
    try:
        results = lookup_crossref(query=query)
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Retrieved {len(results)} records from Crossref."
        })
        
        current_evidence = list(state.get("collected_evidence", []))
        current_evidence, added_count = add_to_evidence(current_evidence, results)
        
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Added {added_count} new records (deduplicated)."
        })
            
        return {
            "collected_evidence": current_evidence,
            "steps": new_steps,
            "next_action": None,
            "next_action_input": None
        }
    except Exception as e:
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Crossref lookup failed: {str(e)}"
        })
        return {"steps": new_steps, "next_action": None, "next_action_input": None}

def analyze_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes the analyze_information tool internally to structure findings.
    """
    new_steps = list(state.get("steps", []))
    new_steps.append({
        "type": "ACTION",
        "content": "analyze_information()"
    })
    
    evidence_list = []
    for idx, ev in enumerate(state.get("collected_evidence", [])):
        source = ev.get("source", "Unknown")
        title = ev.get("title", "No Title")
        if "arXiv" in source:
            evidence_list.append(
                f"Document {idx+1} (arXiv):\nTitle: {title}\nAbstract: {ev.get('abstract', '')}\nURL: {ev.get('pdf_url', '')}"
            )
        else:
            evidence_list.append(
                f"Document {idx+1} (Crossref):\nTitle: {title}\nDOI: {ev.get('doi', '')}\nPublisher: {ev.get('publisher', '')}\nJournal: {ev.get('journal', '')}"
            )
    
    information = "\n\n".join(evidence_list)
    if not information:
        return {"steps": new_steps, "next_action": None, "next_action_input": None}
        
    try:
        analysis = analyze_information(information)
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Information analysis complete. Confidence Score: {analysis.get('confidence_score')}"
        })
        return {
            "analysis_result": analysis,
            "steps": new_steps,
            "next_action": None,
            "next_action_input": None
        }
    except Exception as e:
        new_steps.append({
            "type": "TOOL_RESULT",
            "content": f"Analysis failed: {str(e)}"
        })
        return {"steps": new_steps, "next_action": None, "next_action_input": None}

def compile_report_node(state: AgentState) -> Dict[str, Any]:
    """
    Compiles the final intelligence report based on all evidence and analysis.
    """
    new_steps = list(state.get("steps", []))
    new_steps.append({
        "type": "REASONING_STATUS",
        "content": "Synthesizing findings into final intelligence report..."
    })
    
    objective = state.get("objective", "")
    
    evidence_list = []
    for idx, ev in enumerate(state.get("collected_evidence", [])):
        source = ev.get("source", "Unknown")
        title = ev.get("title", "No Title")
        if "arXiv" in source:
            evidence_list.append(
                f"- **{title}** (arXiv)\n  URL: {ev.get('pdf_url', '')}\n  Abstract: {ev.get('abstract', '')[:300]}..."
            )
        else:
            evidence_list.append(
                f"- **{title}** (Crossref)\n  DOI: {ev.get('doi', '')} | URL: {ev.get('url', '')}\n  Publisher/Journal: {ev.get('publisher') or ev.get('journal') or 'N/A'}"
            )
    evidence_str = "\n".join(evidence_list) if evidence_list else "No external evidence retrieved."
    
    analysis = state.get("analysis_result") or {}
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        report = "# Competitive Intelligence Report\n\nError: Gemini API key is missing."
        new_steps.append({"type": "TASK_COMPLETE", "content": report})
        return {"final_report": report, "steps": new_steps}
        
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.2
        )
        
        prompt = (
            "You are a Principal Competitive Intelligence Officer.\n"
            "Produce a final, structured intelligence report answering the primary objective.\n\n"
            f"Primary Objective: {objective}\n\n"
            "--- GATHERED EVIDENCE ---\n"
            f"{evidence_str}\n\n"
            "--- ANALYSIS SUMMARY ---\n"
            f"Key Developments:\n{json.dumps(analysis.get('key_developments', []), indent=2)}\n"
            f"Opportunities:\n{json.dumps(analysis.get('opportunities', []), indent=2)}\n"
            f"Threats:\n{json.dumps(analysis.get('threats', []), indent=2)}\n"
            f"Trends:\n{json.dumps(analysis.get('trends', []), indent=2)}\n"
            f"Confidence Score: {analysis.get('confidence_score', 'N/A')}\n"
            f"Confidence Justification: {analysis.get('confidence_justification', 'N/A')}\n\n"
            "Draft a comprehensive, publication-quality intelligence report. Use clean markdown. Include sections for:\n"
            "1. Executive Summary\n"
            "2. Strategic Landscape (summarizing key developments and trends)\n"
            "3. Opportunities & Threats (SWOT-style assessment for an organization)\n"
            "4. Research Processing Highlights:\n"
            "   - Rank the retrieved evidence/papers by their relevance to the objective.\n"
            "   - Analyze research trends and identify emerging areas.\n"
            "   - Identify critical research gaps in the literature.\n"
            "5. Operational Recommendations\n"
            "6. Bibliography / Source References (listing urls, titles, DOIs, and arXiv IDs from the evidence above)"
        )
        
        report_response = llm.invoke(prompt)
        report_text = report_response.content
        if isinstance(report_text, list):
            report_text = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in report_text)
            
        new_steps.append({
            "type": "TASK_COMPLETE",
            "content": report_text
        })
        
        return {
            "final_report": report_text,
            "steps": new_steps
        }
    except Exception as e:
        report = f"# Competitive Intelligence Report\n\nFailed to compile due to error: {str(e)}"
        new_steps.append({"type": "TASK_COMPLETE", "content": report})
        return {"final_report": report, "steps": new_steps}

# Graph routing conditional edge
def route_next_action(state: AgentState) -> str:
    """
    Routes to the appropriate tool node or report node.
    """
    next_act = state.get("next_action")
    if next_act == "search_arxiv":
        return "arxiv_node"
    elif next_act == "lookup_crossref":
        return "crossref_node"
    else:
        # Check if we have evidence to analyze first
        if state.get("collected_evidence") and not state.get("analysis_result"):
            return "analyze_node"
        else:
            return "compile_report_node"

# LangGraph Build
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("reasoning", reasoning_node)
workflow.add_node("arxiv_node", arxiv_node)
workflow.add_node("crossref_node", crossref_node)
workflow.add_node("analyze_node", analyze_node)
workflow.add_node("compile_report_node", compile_report_node)

# Set Entry Node
workflow.set_entry_point("reasoning")

# Add Conditional Edges
workflow.add_conditional_edges(
    "reasoning",
    route_next_action,
    {
        "arxiv_node": "arxiv_node",
        "crossref_node": "crossref_node",
        "analyze_node": "analyze_node",
        "compile_report_node": "compile_report_node"
    }
)

# Return back to reasoning
workflow.add_edge("arxiv_node", "reasoning")
workflow.add_edge("crossref_node", "reasoning")
workflow.add_edge("analyze_node", "reasoning")

# Terminal Edge
workflow.add_edge("compile_report_node", END)

# Compile Graph
agent_graph = workflow.compile()
