import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("agent_x.web_search")

def web_search(query: str) -> List[Dict[str, Any]]:
    """
    Performs a web search using Tavily API to gather current industry news, competitor activities,
    product launches, and market developments.
    
    Returns structured results:
    [
      {
        "title": "...",
        "url": "...",
        "source": "...",
        "content": "..."
      }
    ]
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY is not set.")
        return [{
            "title": "Tavily API Key Missing",
            "url": "",
            "source": "tavily",
            "content": "Error: TAVILY_API_KEY environment variable is not configured."
        }]

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=5)
        
        raw_results = response.get("results", [])
        if not raw_results:
            return [{
                "title": "No Results Found",
                "url": "",
                "source": "tavily",
                "content": f"No relevant web search results were found for query: '{query}'."
            }]
            
        structured_results = []
        for item in raw_results:
            structured_results.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "source": item.get("source", "Tavily Web Search"),
                "content": item.get("content", "")
            })
        return structured_results

    except Exception as e:
        logger.error(f"Tavily web search error: {str(e)}")
        return [{
            "title": "Web Search Execution Failure",
            "url": "",
            "source": "tavily",
            "content": f"Failed to execute Tavily web search due to error: {str(e)}"
        }]
