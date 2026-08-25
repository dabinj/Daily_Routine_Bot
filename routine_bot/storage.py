from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS routine_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_date TEXT NOT NULL,
  field TEXT NOT NULL,
  label TEXT NOT NULL,
  value TEXT NOT NULL,
  source TEXT NOT NULL,
  asked_at TEXT,
  answered_at TEXT NOT NULL,
  UNIQUE(entry_date, field)
);

CREATE INDEX IF NOT EXISTS idx_routine_entries_date
ON routine_entries(entry_date);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def upsert_entry(
    db_path: Path,
    entry_date: str,
    field: str,
    label: str,
    value: str,
    source: str,
    asked_at: str | None = None,
) -> None:
    answered_at = datetime.now(timezone.utc).isoformat()
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO routine_entries(entry_date, field, label, value, source, asked_at, answered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entry_date, field) DO UPDATE SET
              label=excluded.label,
              value=excluded.value,
              source=excluded.source,
              asked_at=excluded.asked_at,
              answered_at=excluded.answered_at
            """,
            (entry_date, field, label, value, source, asked_at, answered_at),
        )


def get_day_entries(db_path: Path, entry_date: str) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT entry_date, field, label, value, source, asked_at, answered_at
            FROM routine_entries
            WHERE entry_date = ?
            ORDER BY id
            """,
            (entry_date,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_recent_entries(db_path: Path, days: int = 7, today: str | None = None) -> list[dict[str, Any]]:
    if today:
        cutoff = (datetime.fromisoformat(today) - timedelta(days=days - 1)).date().isoformat()
    else:
        cutoff = f"-{days - 1} day"

    with connect(db_path) as conn:
        if today:
            query = """
            SELECT entry_date, field, label, value, source, asked_at, answered_at
            FROM routine_entries
            WHERE entry_date >= ?
            ORDER BY entry_date DESC, id
            """
            params = (cutoff,)
        else:
            query = """
            SELECT entry_date, field, label, value, source, asked_at, answered_at
            FROM routine_entries
            WHERE entry_date >= date('now', ?)
            ORDER BY entry_date DESC, id
            """
            params = (cutoff,)
        rows = conn.execute(
            query,
            params,
        ).fetchall()
    return [dict(row) for row in rows]
