import urllib.request
import urllib.parse
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("agent_x.crossref_search")

def crossref_search(query: str) -> List[Dict[str, Any]]:
    """
    Queries CrossRef REST API for academic journal articles, conference papers, and DOIs.
    
    Returns structured results:
    [
      {
        "title": "...",
        "authors": ["..."],
        "published_date": "...",
        "summary": "...",
        "url": "...",
        "source": "CrossRef"
      }
    ]
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.crossref.org/works?query={encoded_query}&rows=5"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'NOVAagent/1.0 (mailto:contact@novaagent.org)'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        items = data.get('message', {}).get('items', [])
        if not items:
            return [{
                "title": "No CrossRef Publications Found",
                "authors": [],
                "published_date": "",
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
            summary = f"Published in {journal_name}. Type: {item.get('type', 'journal-article')}."

            results.append({
                "title": title,
                "authors": authors,
                "published_date": published_date,
                "summary": summary,
                "url": paper_url,
                "source": "CrossRef"
            })
            
        return results

    except Exception as e:
        logger.error(f"CrossRef research search error: {str(e)}")
        return [{
            "title": "CrossRef Search Execution Failure",
            "authors": [],
            "published_date": "",
            "summary": f"Failed to execute CrossRef search due to error: {str(e)}",
            "url": "",
            "source": "CrossRef"
        }]
