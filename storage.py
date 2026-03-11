"""
storage.py
Couche de persistance SQLite : save_run(), list_runs(), get_run().
"""

import json
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "runs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée la table runs si elle n'existe pas."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api       TEXT NOT NULL,
                passed    INTEGER NOT NULL,
                failed    INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                latency_avg REAL NOT NULL,
                latency_p95 REAL NOT NULL,
                availability TEXT NOT NULL,
                payload   TEXT NOT NULL
            )
        """)
        conn.commit()


def save_run(run: dict) -> int:
    """Persiste un run complet. Retourne l'id inséré."""
    init_db()
    s = run["summary"]
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO runs
              (timestamp, api, passed, failed, error_rate,
               latency_avg, latency_p95, availability, payload)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                run["timestamp"],
                run["api"],
                s["passed"],
                s["failed"],
                s["error_rate"],
                s["latency_ms_avg"],
                s["latency_ms_p95"],
                s["availability"],
                json.dumps(run),
            ),
        )
        conn.commit()
        return cur.lastrowid


def list_runs(limit: int = 20) -> list:
    """Retourne les N derniers runs (résumé)."""
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, timestamp, api, passed, failed,
                   error_rate, latency_avg, latency_p95, availability
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_run(run_id: int) -> dict | None:
    """Retourne le payload complet d'un run donné."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
    if row:
        return json.loads(row["payload"])
    return None


def get_latest_run() -> dict | None:
    """Retourne le payload du dernier run."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload FROM runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row:
        return json.loads(row["payload"])
    return None
