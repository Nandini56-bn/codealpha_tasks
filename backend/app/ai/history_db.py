"""Simple SQLite generation history."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.utils.config import HISTORY_DB_PATH


def _connect() -> sqlite3.Connection:
    HISTORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(HISTORY_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_request TEXT,
                mode TEXT NOT NULL,
                genre TEXT,
                model TEXT,
                filename TEXT,
                lyrics TEXT,
                metadata TEXT
            )
            """
        )
        conn.commit()


def add_generation(
    *,
    item_id: str,
    mode: str,
    genre: str,
    model: str,
    filename: Optional[str] = None,
    lyrics: Optional[str] = None,
    user_request: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    init_db()
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {
        "id": item_id,
        "timestamp": timestamp,
        "user_request": user_request or "",
        "mode": mode,
        "genre": genre,
        "model": model,
        "filename": filename,
        "lyrics": lyrics,
        "metadata": metadata or {},
    }
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO generations
            (id, timestamp, user_request, mode, genre, model, filename, lyrics, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["id"],
                payload["timestamp"],
                payload["user_request"],
                payload["mode"],
                payload["genre"],
                payload["model"],
                payload["filename"],
                payload["lyrics"],
                json.dumps(payload["metadata"], ensure_ascii=False),
            ),
        )
        conn.commit()
    return payload


def list_generations(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM generations ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    items = []
    for row in rows:
        meta = {}
        try:
            meta = json.loads(row["metadata"] or "{}")
        except Exception:
            meta = {}
        items.append(
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "user_request": row["user_request"],
                "mode": row["mode"],
                "genre": row["genre"],
                "model": row["model"],
                "filename": row["filename"],
                "lyrics": row["lyrics"],
                "metadata": meta,
            }
        )
    return items
