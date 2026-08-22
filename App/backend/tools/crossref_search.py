import urllib.request
import urllib.parse
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("agent_x.crossref_search")

def _determine_quartile(item: Dict[str, Any]) -> str:
    """
    Determines Journal Quartile (Q1, Q2, Q3, Q4) based on CrossRef metadata:
    container title, publisher prestige, and citation/reference counts.
    """
    container = item.get('container-title', [])
    journal_name = (container[0] if container else item.get('publisher', '')).lower()
    is_referenced_by_count = item.get('is-referenced-by-count', 0)
    
    # Q1 Top Impact Journals & Publishers
    q1_keywords = ["nature", "ieee", "acm", "elsevier", "springer", "cell", "lancet", "science", "oxford", "cambridge", "mit", "stanford", "return on intelligence"]
    if any(k in journal_name for k in q1_keywords) or is_referenced_by_count >= 10:
        return "Q1"
        
    # Q2 High Impact Journals
    q2_keywords = ["wiley", "taylor", "sage", "frontiers", "mdpi", "al qasimi", "journal", "transactions"]
    if any(k in journal_name for k in q2_keywords) or is_referenced_by_count >= 3:
        return "Q2"
        
    # Q3 Working papers / proceedings
    if "ssrn" in journal_name or "proceedings" in journal_name:
        return "Q3"
        
    return "Q4"

def crossref_search(query: str, year: Optional[str] = None, timeframe: Optional[str] = None, quartile: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Queries CrossRef REST API for academic journal articles, conference papers, and DOIs.
    Enriches each paper with quartile metadata (Q1, Q2, Q3, Q4) and filters accordingly.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.crossref.org/works?query={encoded_query}&rows=12"
        if year and year != "Any Year" and year.isdigit():
            url += f"&filter=from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"

        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'NOVAagent/1.0 (mailto:contact@novaagent.org)'
            }
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

        items = data.get('message', {}).get('items', [])
        if not items:
            return [{
                "title": "No CrossRef Publications Found",
                "authors": [],
                "published_date": "",
                "quartile": "Q4",
                "summary": f"No CrossRef academic publications found for query: '{query}'.",
                "url": "",
                "source": "CrossRef"
            }]

        results = []
        for item in items:
            titles = item.get('title', [])
            title = titles[0].strip() if titles else "Untitled Publication"
            
            # Extract authors
            authors = []
            for author in item.get('author', []):
                given = author.get('given', '')
                family = author.get('family', '')
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)
            
            # Published Date
            published_date = ""
            date_parts = item.get('published-print', {}).get('date-parts', []) or item.get('published-online', {}).get('date-parts', [])
            if date_parts and date_parts[0]:
                published_date = "-".join(str(p) for p in date_parts[0])
            
            # URL / DOI
            paper_url = item.get('URL', '') or f"https://doi.org/{item.get('DOI', '')}"
            
            # Container / Publisher Summary
            container = item.get('container-title', [])
            publisher = item.get('publisher', '')
            journal_name = container[0] if container else publisher
            pub_type = item.get('type', 'journal-article')
            
            q_rating = _determine_quartile(item)
            
            # Filter by quartile if requested
            if quartile and quartile not in ["All Quartiles", ""] and q_rating != quartile:
                continue

            summary = f"Published in {journal_name} ({q_rating} Journal). Type: {pub_type}."

            results.append({
                "title": title,
                "authors": authors,
                "published_date": published_date,
                "quartile": q_rating,
                "summary": summary,
                "url": paper_url,
                "source": "CrossRef"
            })
            
        return results if results else [{
            "title": f"No CrossRef Papers Found for Quartile {quartile}",
            "authors": [],
            "published_date": year if year else "",
            "quartile": quartile if quartile else "Q4",
            "summary": f"No papers matched the requested quartile filter: {quartile}.",
            "url": "",
            "source": "CrossRef"
        }]

    except Exception as e:
        logger.error(f"CrossRef research search error: {str(e)}")
        return [{
            "title": "CrossRef Search Execution Failure",
            "authors": [],
            "published_date": "",
            "quartile": "Q4",
            "summary": f"Failed to execute CrossRef search due to error: {str(e)}",
            "url": "",
            "source": "CrossRef"
        }]
