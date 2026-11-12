import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("omnisight.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().isoformat(timespec="seconds")


def init_db():
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commit_sha TEXT, bug TEXT, status TEXT, message TEXT,
                created_at TEXT, finished_at TEXT
            );
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER, page TEXT, viewport TEXT,
                issue_type TEXT, severity TEXT, description TEXT,
                fix_json TEXT, status TEXT, attempts INTEGER,
                before_img TEXT, after_img TEXT,
                review TEXT DEFAULT 'pending',
                pr_url TEXT, pr_number INTEGER
            );
            """
        )


def migrate():
    """Purani database mein naye columns jodta hai (agar pehle se hain to chhod deta hai)."""
    with _conn() as c:
        for col in ("pr_url TEXT", "pr_number INTEGER"):
            try:
                c.execute(f"ALTER TABLE findings ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass


def create_run(commit_sha, bug):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO runs (commit_sha, bug, status, created_at) VALUES (?,?,?,?)",
            (commit_sha, bug, "queued", now()),
        )
        return cur.lastrowid


def update_run(run_id, status, message=None):
    finished = now() if status in ("done", "failed") else None
    with _conn() as c:
        c.execute(
            "UPDATE runs SET status=?, message=?, finished_at=? WHERE id=?",
            (status, message, finished, run_id),
        )


def add_finding(run_id, page, viewport, issue_type, severity, description,
                fix_json, status, attempts, before_img, after_img):
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO findings (run_id, page, viewport, issue_type, severity,
               description, fix_json, status, attempts, before_img, after_img)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (run_id, page, viewport, issue_type, severity, description,
             fix_json, status, attempts, before_img, after_img),
        )
        return cur.lastrowid


def set_pr(finding_id, pr_url, pr_number):
    with _conn() as c:
        c.execute(
            "UPDATE findings SET pr_url=?, pr_number=? WHERE id=?",
            (pr_url, pr_number, finding_id),
        )


def list_runs():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM runs ORDER BY id DESC")]


def get_run(run_id):
    with _conn() as c:
        run = c.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if run is None:
            return None
        findings = c.execute("SELECT * FROM findings WHERE run_id=?", (run_id,)).fetchall()
        return {**dict(run), "findings": [dict(f) for f in findings]}


def get_finding(finding_id):
    with _conn() as c:
        row = c.execute("SELECT * FROM findings WHERE id=?", (finding_id,)).fetchone()
        return dict(row) if row else None


def set_review(finding_id, review):
    with _conn() as c:
        c.execute("UPDATE findings SET review=? WHERE id=?", (review, finding_id))