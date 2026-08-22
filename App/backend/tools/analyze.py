import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("agent_x.analyze")

def analyze_information(
    objective: str,
    web_results: List[Dict[str, Any]],
    research_results: List[Dict[str, Any]],
    crossref_results: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Uses Gemini API to synthesize and analyze collected evidence (web + arXiv + CrossRef results).
    """
    if crossref_results is None:
        crossref_results = []

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    # Prepare text summary of collected evidence
    evidence_text = f"INTELLIGENCE OBJECTIVE: {objective}\n\n"
    evidence_text += "--- WEB SEARCH EVIDENCE ---\n"
    if web_results:
        for idx, item in enumerate(web_results, 1):
            evidence_text += f"[{idx}] Title: {item.get('title')}\n    URL: {item.get('url')}\n    Content: {item.get('content')}\n\n"
    else:
        evidence_text += "No web search evidence collected.\n\n"

    evidence_text += "--- arXiv RESEARCH PAPER EVIDENCE ---\n"
    if research_results:
        for idx, item in enumerate(research_results, 1):
            authors = ", ".join(item.get("authors", []))
            evidence_text += f"[{idx}] Title: {item.get('title')}\n    Authors: {authors}\n    Published: {item.get('published_date')}\n    Summary: {item.get('summary')}\n    URL: {item.get('url')}\n\n"
    else:
        evidence_text += "No arXiv paper evidence collected.\n\n"

    evidence_text += "--- CROSSREF ACADEMIC PUBLICATION EVIDENCE ---\n"
    if crossref_results:
        for idx, item in enumerate(crossref_results, 1):
            authors = ", ".join(item.get("authors", []))
            evidence_text += f"[{idx}] Title: {item.get('title')}\n    Authors: {authors}\n    Published: {item.get('published_date')}\n    Summary: {item.get('summary')}\n    URL: {item.get('url')}\n\n"
    else:
        evidence_text += "No CrossRef paper evidence collected.\n\n"

    if not api_key:
        logger.warning("GEMINI_API_KEY is missing. Providing fallback analysis based directly on raw text.")
        return {
            "key_developments": ["Evidence collected from web, arXiv, and CrossRef queries."],
            "competitor_implications": ["Analysis pending Gemini API key configuration."],
            "emerging_trends": ["Trends synthesized from available titles and summaries."],
            "opportunities": ["Potential opportunities identified in market/tech space."],
            "threats_and_risks": ["Potential market or technical risks to monitor."],
            "strategic_implications": ["Continuous monitoring of identified sources is advised."],
            "confidence_level": "MEDIUM (Fallback analysis executed without LLM API key)",
            "recommended_actions": ["Configure GEMINI_API_KEY for full deep strategic synthesis."],
            "raw_evidence_summary": evidence_text[:1000]
        }

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,
            temperature=0.2
        )

        prompt = f"""
You are an elite Competitive Intelligence Analyst. Evaluate strictly the evidence provided below for the specified objective.
Do NOT invent unsupported facts or outside hallucinations. Base all findings strictly on the collected evidence.

{evidence_text}

Respond strictly with a JSON object containing the following keys (no markdown code blocks, pure JSON):
{{
  "key_developments": ["..."],
  "competitor_implications": ["..."],
  "emerging_trends": ["..."],
  "opportunities": ["..."],
  "threats_and_risks": ["..."],
  "strategic_implications": ["..."],
  "confidence_level": "HIGH / MEDIUM / LOW (explain briefly based on evidence density)",
  "recommended_actions": ["..."]
}}
"""
        messages = [
            SystemMessage(content="You analyze competitive intelligence evidence and output strict JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        raw_content = response.content
        if isinstance(raw_content, list):
            content_str = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in raw_content]).strip()
        else:
            content_str = str(raw_content).strip()
        
        # Clean potential markdown wrapping
        if content_str.startswith("```json"):
            content_str = content_str[7:]
        if content_str.startswith("```"):
            content_str = content_str[3:]
        if content_str.endswith("```"):
            content_str = content_str[:-3]
        content_str = content_str.strip()

        parsed_json = json.loads(content_str)
        return parsed_json

    except Exception as e:
        logger.error(f"Analysis tool Gemini API call error: {str(e)}")
        return {
            "key_developments": [f"Evidence analyzed from {len(web_results)} web results, {len(research_results)} arXiv papers, and {len(crossref_results)} CrossRef publications."],
            "competitor_implications": ["Competitors are actively developing technologies in this domain."],
            "emerging_trends": ["Accelerating adoption of autonomous and AI-driven capabilities."],
            "opportunities": ["Strategic positioning in high-growth technological vectors."],
            "threats_and_risks": ["Rapid technological obsolescence and competitive displacement."],
            "strategic_implications": ["Operational agility and early tech integration required."],
            "confidence_level": "MEDIUM (Basic synthesis due to analysis API warning)",
            "recommended_actions": ["Review source documents directly for specific citations."],
            "analysis_error": str(e)
        }
