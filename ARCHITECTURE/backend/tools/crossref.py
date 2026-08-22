import urllib.request
import urllib.parse
import urllib.error
import json
import re
import time
from typing import List, Dict, Any, Optional

def lookup_crossref(query: str) -> List[Dict[str, Any]]:
    """
    Search and verify publication details using Crossref API.
    
    Args:
        query: DOI string or paper title query.
        
    Returns:
        List of normalized Crossref paper dictionaries.
    """
    if not query or not query.strip():
        return []
        
    query_str = query.strip()
    # Check if query is a DOI
    is_doi = bool(re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', query_str, re.IGNORECASE))
    
    if is_doi:
        url = f"https://api.crossref.org/works/{urllib.parse.quote(query_str)}"
    else:
        url = f"https://api.crossref.org/works?query={urllib.parse.quote(query_str)}&rows=5"
        
    headers = {"User-Agent": "AgentXCompetitiveIntelligence/1.0 (mailto:agentx@example.com)"}
    
    max_retries = 3
    backoff = 1.0
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                
            if data.get("status") != "ok":
                return []
                
            message = data.get("message", {})
            if is_doi:
                items = [message]
            else:
                items = message.get("items", [])
                
            results = []
            for item in items:
                title = item.get("title", [""])[0] if item.get("title") else ""
                
                authors = []
                for auth in item.get("author", []):
                    given = auth.get("given", "")
                    family = auth.get("family", "")
                    if given or family:
                        authors.append(f"{given} {family}".strip())
                    elif "name" in auth:
                        authors.append(auth["name"])
                        
                doi = item.get("DOI", "")
                
                # Extract date
                parts = item.get("published", {}).get("date-parts", [[None]])[0]
                if not parts or parts[0] is None:
                    parts = item.get("created", {}).get("date-parts", [[None]])[0]
                    
                if parts and parts[0] is not None:
                    year = parts[0]
                    month = parts[1] if len(parts) > 1 else 1
                    day = parts[2] if len(parts) > 2 else 1
                    published_date = f"{year:04d}-{month:02d}-{day:02d}"
                else:
                    published_date = ""
                    
                container = item.get("container-title", [""])
                container_title = container[0] if container else ""
                
                w_type = item.get("type", "")
                journal = ""
                conference = ""
                if "journal" in w_type or w_type == "journal-article":
                    journal = container_title
                elif "proceedings" in w_type or "conference" in w_type or w_type == "proceedings-article":
                    conference = container_title
                else:
                    journal = container_title
                    
                publisher = item.get("publisher", "")
                url_val = item.get("URL", f"https://doi.org/{doi}" if doi else "")
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "doi": doi,
                    "published_date": published_date,
                    "journal": journal,
                    "conference": conference,
                    "publisher": publisher,
                    "url": url_val,
                    "source": "Crossref"
                })
            return results
        except urllib.error.HTTPError as e:
            # Handle rate limiting (429) or temporary server errors (5xx)
            if e.code == 429 or e.code >= 500:
                if attempt < max_retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                    continue
            raise RuntimeError(f"Crossref API HTTP {e.code} error: {e.reason}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise RuntimeError(f"Crossref API connection failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Crossref API returned malformed JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Crossref API unexpected error: {str(e)}")
    
    return []

