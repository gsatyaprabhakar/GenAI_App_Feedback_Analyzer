"""
All the database work lives here (Lesson 12).

Keeping the database code in its own file.
streamlit_app.py just imports these functions and uses them.
"""

import sqlite3
from pathlib import Path
from typing import Iterable, Mapping

# Keep the database in the project root, regardless of the process working directory.
DB_FILE = Path(__file__).resolve().parents[2] / "feedback.db"


def init_db() -> None:
    """Create the feedback table the first time we run."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                review TEXT NOT NULL,
                label TEXT NOT NULL,
                score INTEGER NOT NULL,
                theme TEXT NOT NULL
            )
        """)


def save_results(results: Iterable[Mapping[str, object]]) -> int:
    """Write all analyzed reviews into the database."""
    rows = [
        (r["review"], r["label"], r["score"], r["theme"])
        for r in results
        if r.get("label") != "error"
    ]
    if not rows:
        return 0

    with sqlite3.connect(DB_FILE) as conn:
        conn.executemany(
            "INSERT INTO feedback (review, label, score, theme) VALUES (?, ?, ?, ?)",
            rows,
        )
    return len(rows)


def load_history():
    """Read every review we have saved so far."""
    with sqlite3.connect(DB_FILE) as conn:
        return conn.execute(
            "SELECT review, label, score, theme FROM feedback "
            "ORDER BY id DESC"
        ).fetchall()
