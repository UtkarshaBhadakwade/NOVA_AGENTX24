import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger("agent_x.research_search")

def _sanitize_arxiv_query(query: str) -> str:
    """
    Cleans long sentences into concise search terms suitable for arXiv API search.
    """
    words = query.split()
    if len(words) > 6:
        stop_words = {"find", "the", "latest", "developments", "in", "and", "determine", "whether", "they", "represent", "an", "opportunity", "or", "threat", "for", "organization", "a", "of", "to", "is"}
        filtered = [w for w in words if w.lower().strip(".,?!\"'") not in stop_words]
        if filtered:
            return " ".join(filtered[:5])
        return "AI agents"
    return query

def _determine_arxiv_quartile(entry: ET.Element, ns: dict) -> str:
    """
    Classifies arXiv paper into Q1, Q2, Q3 based on primary categories, comment metadata, and journal references.
    """
    comment_elem = entry.find('atom:comment', ns)
    comment = comment_elem.text.lower() if comment_elem is not None and comment_elem.text else ""
    
    journal_ref_elem = entry.find('arxiv:journal_ref', {'arxiv': 'http://arxiv.org/schemas/atom'})
    journal_ref = journal_ref_elem.text.lower() if journal_ref_elem is not None and journal_ref_elem.text else ""
    
    # If published in recognized peer-reviewed venue or accepted to top conference (NeurIPS, ICML, ICLR, AAAI, ACL)
    top_venues = ["neurips", "icml", "iclr", "aaai", "acl", "cvpr", "eccv", "iccv", "nature", "ieee", "acm"]
    if any(v in comment for v in top_venues) or any(v in journal_ref for v in top_venues):
        return "Q1"
        
    # High impact AI/ML categories on arXiv (cs.AI, cs.CL, cs.LG, cs.SE, cs.CR)
    categories = [c.attrib.get('term', '') for c in entry.findall('atom:category', ns)]
    if any(cat in ["cs.AI", "cs.CL", "cs.LG", "cs.CR", "cs.SE"] for cat in categories):
        return "Q1"
    elif any(cat.startswith("cs.") for cat in categories):
        return "Q2"
        
    return "Q3"

def research_search(query: str, year: Optional[str] = None, timeframe: Optional[str] = None, quartile: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Queries arXiv API for scientific papers, technical research, and academic publications.
    Enriches each paper with quartile metadata (Q1, Q2, Q3, Q4) and filters accordingly.
    """
    clean_q = _sanitize_arxiv_query(query)
    
    if year and year != "Any Year" and year.isdigit():
        search_term = f'all:"{clean_q}" AND submittedDate:[{year}01010000 TO {year}12312359]'
    else:
        search_term = f'all:"{clean_q}"' if " " in clean_q else f'all:{clean_q}'

    try:
        encoded_query = urllib.parse.quote(search_term)
        url = f"http://export.arxiv.org/api/query?search_query={encoded_query}&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'NOVAagent-CompetitiveIntelligence/1.0'}
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            fallback_url = "http://export.arxiv.org/api/query?search_query=all:%22AI%20agents%22&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
            fallback_req = urllib.request.Request(fallback_url, headers={'User-Agent': 'NOVAagent-CompetitiveIntelligence/1.0'})
            with urllib.request.urlopen(fallback_req, timeout=10) as response:
                xml_data = response.read()
            root = ET.fromstring(xml_data)
            entries = root.findall('atom:entry', ns)

        if not entries:
            return [{
                "title": "No Research Papers Found",
                "authors": [],
                "published_date": "",
                "quartile": "Q1",
                "summary": f"No arXiv research publications found matching query: '{query}'.",
                "url": "",
                "source": "arXiv"
            }]

        results = []
        for entry in entries:
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None and title_elem.text else "Untitled Paper"
            
            published_elem = entry.find('atom:published', ns)
            published_date = published_elem.text[:10] if published_elem is not None and published_elem.text else ""
            
            if year and year != "Any Year" and year.isdigit() and published_date:
                if not published_date.startswith(year):
                    continue

            summary_elem = entry.find('atom:summary', ns)
            summary = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None and summary_elem.text else ""
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
                    
            id_elem = entry.find('atom:id', ns)
            paper_url = id_elem.text.strip() if id_elem is not None and id_elem.text else ""

            q_rating = _determine_arxiv_quartile(entry, ns)

            if quartile and quartile not in ["All Quartiles", ""] and q_rating != quartile:
                continue

            results.append({
                "title": title,
                "authors": authors,
                "published_date": published_date,
                "quartile": q_rating,
                "summary": f"({q_rating} Impact) {summary}",
                "url": paper_url,
                "source": "arXiv"
            })
            
        return results if results else [{
            "title": f"No arXiv Research Papers Found for Quartile {quartile}",
            "authors": [],
            "published_date": year if year else "",
            "quartile": quartile if quartile else "Q1",
            "summary": f"No papers matched the requested quartile filter: {quartile}.",
            "url": "",
            "source": "arXiv"
        }]

    except Exception as e:
        logger.error(f"arXiv research search error: {str(e)}")
        return [{
            "title": "Research Search Execution Failure",
            "authors": [],
            "published_date": "",
            "quartile": "Q1",
            "summary": f"Failed to execute arXiv research search due to error: {str(e)}",
            "url": "",
            "source": "arXiv"
        }]
