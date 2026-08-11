"""SQLite永続化層"""

import csv
import io
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"

CSV_HEADERS = [
    "id",
    "created_at",
    "score_nature",
    "score_inquiry",
    "score_creativity",
    "score_cooperation",
    "score_action",
    "hero_type",
    "answers",
    "user_agent",
]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # WALモード：書き込み中も他の接続が読み取り可能になり、イベント当日の同時アクセスに強くなる
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                answers TEXT NOT NULL,
                score_nature INTEGER NOT NULL,
                score_inquiry INTEGER NOT NULL,
                score_creativity INTEGER NOT NULL,
                score_cooperation INTEGER NOT NULL,
                score_action INTEGER NOT NULL,
                hero_type TEXT NOT NULL,
                user_agent TEXT
            )
            """
        )


def save_response(
    answers: list[int],
    scores: dict[str, int],
    hero_type: str,
    user_agent: str | None,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO responses (
                created_at, answers,
                score_nature, score_inquiry, score_creativity, score_cooperation, score_action,
                hero_type, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                json.dumps(answers, ensure_ascii=False),
                scores["nature"],
                scores["inquiry"],
                scores["creativity"],
                scores["cooperation"],
                scores["action"],
                hero_type,
                user_agent,
            ),
        )
        return cursor.lastrowid


def list_responses() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM responses ORDER BY id DESC"
        ).fetchall()


def export_csv() -> str:
    rows = list_responses()
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_HEADERS)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row[key] for key in CSV_HEADERS})
    return buffer.getvalue()
