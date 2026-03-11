import sqlite3
import json
from datetime import datetime

DB_PATH = "runs.db"

def init_db():
    """Crée la table si elle n'existe pas encore."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                passed    INTEGER,
                failed    INTEGER,
                error_rate REAL,
                latency_avg INTEGER,
                latency_p95 INTEGER,
                details   TEXT
            )
        """)

def save_run(run):
    """Enregistre un run complet en base."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO runs 
            (timestamp, passed, failed, error_rate, latency_avg, latency_p95, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run["timestamp"],
            run["summary"]["passed"],
            run["summary"]["failed"],
            run["summary"]["error_rate"],
            run["summary"]["latency_ms_avg"],
            run["summary"]["latency_ms_p95"],
            json.dumps(run["tests"])  # on stocke le détail des tests en JSON
        ))

def list_runs(limit=20):
    """Retourne les derniers runs (du plus récent au plus ancien)."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM runs ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "passed": row["passed"],
            "failed": row["failed"],
            "error_rate": row["error_rate"],
            "latency_avg": row["latency_avg"],
            "latency_p95": row["latency_p95"],
            "tests": json.loads(row["details"])
        })
    return result