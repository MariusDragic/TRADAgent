from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from tradagent.models import Decision


@dataclass(frozen=True)
class SQLiteMemory:
    db_path: str

    def init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts_utc TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    decision_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_decision(self, ticker: str, decision: Decision) -> None:
        payload = decision.model_dump()
        ts_utc = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO decisions (ts_utc, ticker, decision_json) VALUES (?, ?, ?)",
                (ts_utc, ticker, json.dumps(payload)),
            )
            conn.commit()

    def recent_decisions(self, ticker: str, limit: int = 5) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """
                SELECT ts_utc, decision_json
                FROM decisions
                WHERE ticker = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (ticker, limit),
            )
            rows = cur.fetchall()

        out: list[dict[str, Any]] = []
        for ts_utc, decision_json in rows:
            item = {"ts_utc": ts_utc, "decision": json.loads(decision_json)}
            out.append(item)
        return out
