import json
from typing import List

import aiosqlite

from app.storage.base import AuditRepo


def _row(row) -> dict:
    d = dict(row)
    d["details"] = json.loads(d.get("details") or "{}")
    return d


class SQLiteAuditRepo(AuditRepo):
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def insert(self, doc: dict) -> None:
        await self._conn.execute(
            """INSERT INTO audit_logs (id, user_id, username, action, entity, entity_id, details, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                doc["id"], doc["user_id"], doc["username"], doc["action"],
                doc["entity"], doc["entity_id"],
                json.dumps(doc.get("details") or {}),
                doc["timestamp"],
            ),
        )
        await self._conn.commit()

    async def list_recent(self, limit: int = 100) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
        ) as cur:
            rows = await cur.fetchall()
        return [_row(r) for r in rows]
