import time
from typing import List, Dict, Any, Optional
import arxiv

def search_arxiv(
    query: str,
    max_results: int = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Search research papers using arXiv API.
    
    Args:
        query: Search query string.
        max_results: Maximum number of papers to retrieve.
        year_from: Start year for date filtering.
        year_to: End year for date filtering.
        
    Returns:
        List of normalized research paper dictionaries.
    """
    if not query or not query.strip():
        return []
        
    full_query = query.strip()
    if year_from or year_to:
        s_yr = year_from or 1990
        e_yr = year_to or 2026
        full_query = f"({full_query}) AND submittedDate:[{s_yr}01010000 TO {e_yr}12312359]"
        
    max_retries = 3
    backoff = 1.0
    
    for attempt in range(max_retries):
        try:
            client = arxiv.Client(num_retries=3)
            search = arxiv.Search(
                query=full_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            results = []
            for result in client.results(search):
                # Extract basic ID from full entry URL
                arxiv_id = result.entry_id.split("/abs/")[-1] if "/abs/" in result.entry_id else result.entry_id
                
                results.append({
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "published_date": result.published.strftime("%Y-%m-%d") if result.published else "",
                    "updated_date": result.updated.strftime("%Y-%m-%d") if result.updated else "",
                    "arxiv_id": arxiv_id,
                    "pdf_url": result.pdf_url,
                    "categories": result.categories,
                    "source": "arXiv"
                })
            return results
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise RuntimeError(f"arXiv search failed after {max_retries} attempts: {str(e)}")

