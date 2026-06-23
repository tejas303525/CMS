from typing import List, Optional

import aiosqlite

from app.storage.base import UserRepo


def _row(row, include_hash: bool = False) -> dict:
    d = dict(row)
    d["is_active"] = bool(d["is_active"])
    if not include_hash:
        d.pop("password_hash", None)
    return d


class SQLiteUserRepo(UserRepo):
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        async with self._conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
        return _row(row) if row else None

    async def get_by_username(self, username: str) -> Optional[dict]:
        async with self._conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ) as cur:
            row = await cur.fetchone()
        return _row(row, include_hash=True) if row else None

    async def list_all(self) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ) as cur:
            rows = await cur.fetchall()
        return [_row(r) for r in rows]

    async def create(self, doc: dict) -> None:
        await self._conn.execute(
            """INSERT INTO users (id, username, password_hash, full_name, role, is_active, last_login, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                doc["id"], doc["username"], doc["password_hash"], doc["full_name"],
                doc["role"], int(doc.get("is_active", True)), doc.get("last_login"),
                doc["created_at"],
            ),
        )
        await self._conn.commit()

    async def update(self, user_id: str, fields: dict) -> Optional[dict]:
        if not fields:
            return await self.get_by_id(user_id)
        serialized = {k: (int(v) if k == "is_active" else v) for k, v in fields.items()}
        sets = ", ".join(f"{k} = ?" for k in serialized)
        vals = list(serialized.values()) + [user_id]
        cur = await self._conn.execute(f"UPDATE users SET {sets} WHERE id = ?", vals)
        if cur.rowcount == 0:
            await self._conn.rollback()
            return None
        await self._conn.commit()
        return await self.get_by_id(user_id)

    async def delete(self, user_id: str) -> None:
        await self._conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await self._conn.commit()

    async def touch_login(self, user_id: str, ts: str) -> None:
        await self._conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?", (ts, user_id)
        )
        await self._conn.commit()
