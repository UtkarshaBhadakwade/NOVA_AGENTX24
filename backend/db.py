import sqlite3
import json
import uuid
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("nova_agent.db")

def get_db_path() -> str:
    """
    Returns writable DB path. Uses /tmp on Vercel / Serverless read-only environments.
    """
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "/tmp/investigations.db"
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    if not os.access(base_dir, os.W_OK):
        return "/tmp/investigations.db"
        
    return os.path.join(base_dir, "investigations.db")

def get_db_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        db_path = get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                timeframe TEXT DEFAULT 'Latest',
                year TEXT DEFAULT 'Any Year',
                source_filter TEXT DEFAULT 'All Sources',
                quartile TEXT DEFAULT 'All Quartiles',
                status TEXT NOT NULL,
                iterations INTEGER DEFAULT 0,
                tools_called TEXT,
                trace_events TEXT,
                final_report TEXT,
                web_results_count INTEGER DEFAULT 0,
                research_results_count INTEGER DEFAULT 0,
                crossref_results_count INTEGER DEFAULT 0,
                pinned INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
        """)
        
        # Migration: Ensure quartile column exists in pre-existing DB tables
        cursor.execute("PRAGMA table_info(investigations)")
        columns = [col["name"] for col in cursor.fetchall()]
        if "quartile" not in columns:
            cursor.execute("ALTER TABLE investigations ADD COLUMN quartile TEXT DEFAULT 'All Quartiles';")

        conn.commit()
        conn.close()
        logger.info(f"SQLite database initialized at {db_path}")
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Persistent database initialization warning: {str(e)}")

def save_investigation(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inv_id = str(uuid.uuid4())[:8]
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        objective = data.get("objective", "")
        timeframe = data.get("timeframe", "Latest")
        year = data.get("year", "Any Year")
        source_filter = data.get("source_filter", "All Sources")
        quartile = data.get("quartile", "All Quartiles")
        status = data.get("status", "completed")
        iterations = data.get("iterations", 0)
        tools_called = json.dumps(data.get("tools_called", []))
        trace_events = json.dumps(data.get("trace_events", []))
        final_report = json.dumps(data.get("final_report", {}))
        web_results_count = data.get("web_results_count", 0)
        research_results_count = data.get("research_results_count", 0)
        crossref_results_count = data.get("crossref_results_count", 0)
        pinned = 0

        cursor.execute("""
            INSERT INTO investigations (
                id, objective, timeframe, year, source_filter, quartile, status, iterations,
                tools_called, trace_events, final_report, web_results_count,
                research_results_count, crossref_results_count, pinned, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inv_id, objective, timeframe, year, source_filter, quartile, status, iterations,
            tools_called, trace_events, final_report, web_results_count,
            research_results_count, crossref_results_count, pinned, created_at
        ))
        
        conn.commit()
        conn.close()
        
        result = dict(data)
        result["id"] = inv_id
        result["created_at"] = created_at
        result["pinned"] = False
        return result
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Failed to save investigation history: {str(e)}")
        return None

def get_investigations(limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, objective, timeframe, year, source_filter, quartile, status, iterations,
                   web_results_count, research_results_count, crossref_results_count,
                   pinned, created_at
            FROM investigations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        pinned_list = []
        recent_list = []
        
        for row in rows:
            item = {
                "id": row["id"],
                "objective": row["objective"],
                "timeframe": row["timeframe"],
                "year": row["year"],
                "source_filter": row["source_filter"],
                "quartile": row["quartile"] if "quartile" in row.keys() else "All Quartiles",
                "status": row["status"],
                "iterations": row["iterations"],
                "web_results_count": row["web_results_count"],
                "research_results_count": row["research_results_count"],
                "crossref_results_count": row["crossref_results_count"],
                "pinned": bool(row["pinned"]),
                "created_at": row["created_at"]
            }
            if item["pinned"]:
                pinned_list.append(item)
            else:
                recent_list.append(item)
                
        return {"pinned": pinned_list, "recent": recent_list}
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Failed to fetch investigations: {str(e)}")
        return {"pinned": [], "recent": []}

def get_investigation_by_id(inv_id: str) -> Optional[Dict[str, Any]]:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM investigations WHERE id = ?", (inv_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return {
            "id": row["id"],
            "objective": row["objective"],
            "timeframe": row["timeframe"],
            "year": row["year"],
            "source_filter": row["source_filter"],
            "quartile": row["quartile"] if "quartile" in row.keys() else "All Quartiles",
            "status": row["status"],
            "iterations": row["iterations"],
            "tools_called": json.loads(row["tools_called"] or "[]"),
            "trace_events": json.loads(row["trace_events"] or "[]"),
            "final_report": json.loads(row["final_report"] or "{}"),
            "web_results_count": row["web_results_count"],
            "research_results_count": row["research_results_count"],
            "crossref_results_count": row["crossref_results_count"],
            "pinned": bool(row["pinned"]),
            "created_at": row["created_at"]
        }
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Failed to fetch investigation {inv_id}: {str(e)}")
        return None

def search_investigations(query: str) -> List[Dict[str, Any]]:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        pattern = f"%{query.strip()}%"
        cursor.execute("""
            SELECT id, objective, timeframe, year, source_filter, quartile, status, iterations,
                   web_results_count, research_results_count, crossref_results_count,
                   pinned, created_at
            FROM investigations
            WHERE objective LIKE ? OR final_report LIKE ?
            ORDER BY created_at DESC
            LIMIT 30
        """, (pattern, pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "objective": row["objective"],
                "timeframe": row["timeframe"],
                "year": row["year"],
                "source_filter": row["source_filter"],
                "quartile": row["quartile"] if "quartile" in row.keys() else "All Quartiles",
                "status": row["status"],
                "iterations": row["iterations"],
                "web_results_count": row["web_results_count"],
                "research_results_count": row["research_results_count"],
                "crossref_results_count": row["crossref_results_count"],
                "pinned": bool(row["pinned"]),
                "created_at": row["created_at"]
            })
        return results
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Failed to search investigations: {str(e)}")
        return []

def toggle_pinned(inv_id: str) -> bool:
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT pinned FROM investigations WHERE id = ?", (inv_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
            
        new_pinned = 0 if row["pinned"] else 1
        cursor.execute("UPDATE investigations SET pinned = ? WHERE id = ?", (new_pinned, inv_id))
        conn.commit()
        conn.close()
        return bool(new_pinned)
    except Exception as e:
        logger.warning(f"[MEMORY_WARNING] Failed to toggle pin: {str(e)}")
        return False
