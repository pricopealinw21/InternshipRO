import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                company    TEXT NOT NULL,
                location   TEXT,
                url        TEXT UNIQUE,
                source     TEXT,
                tags       TEXT,
                posted_at  TEXT,
                scraped_at TEXT
            )
        """)

def upsert_jobs(jobs: list[dict]):
    with get_conn() as conn:
        for job in jobs:
            conn.execute("""
                INSERT INTO jobs (title, company, location, url, source, tags, posted_at, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title      = excluded.title,
                    scraped_at = excluded.scraped_at
            """, (
                job["title"], job["company"], job.get("location", ""),
                job.get("url", ""), job.get("source", ""),
                json.dumps(job.get("tags", []), ensure_ascii=False),
                job.get("posted_at", datetime.now().isoformat()),
                datetime.now().isoformat()
            ))

def get_jobs() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY posted_at DESC"
        ).fetchall()
    result = []
    for r in rows:
        job = dict(r)
        job["tags"] = json.loads(job["tags"] or "[]")
        result.append(job)
    return result

def get_stats() -> dict:
    today = datetime.now().date().isoformat()
    with get_conn() as conn:
        total     = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        today_cnt = conn.execute("SELECT COUNT(*) FROM jobs WHERE posted_at LIKE ?", (f"{today}%",)).fetchone()[0]
        companies = conn.execute("SELECT COUNT(DISTINCT company) FROM jobs").fetchone()[0]
    return {"total": total, "today": today_cnt, "companies": companies}

init_db()
