import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("agent_x.web_search")

def web_search(query: str, year: Optional[str] = None, timeframe: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Queries Tavily Search API for live web market news, competitor developments, and industry updates.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY environment variable is missing.")
        return [{
            "title": "Tavily API Key Missing",
            "url": "",
            "content": "TAVILY_API_KEY environment variable is not configured. Web search results are unavailable.",
            "source": "Tavily"
        }]

    # Refine query with year/timeframe context if specified
    search_query = query
    if year and year != "Any Year":
        search_query += f" {year}"

    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=api_key)
        
        # Convert timeframe to Tavily search_depth or days if supported
        response = tavily.search(query=search_query, max_results=5, search_depth="advanced")
        
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Untitled Web Result"),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "published_date": item.get("published_date", year if year else ""),
                "source": "Tavily"
            })
            
        if not results:
            return [{
                "title": "No Web Search Results Found",
                "url": "",
                "content": f"No Tavily web search results found for query: '{search_query}'.",
                "published_date": "",
                "source": "Tavily"
            }]
            
        return results

    except Exception as e:
        logger.error(f"Tavily search execution error: {str(e)}")
        return [{
            "title": "Web Search Execution Failure",
            "url": "",
            "content": f"Failed to execute Tavily web search due to error: {str(e)}",
            "published_date": "",
            "source": "Tavily"
        }]
