import json
from typing import List, Optional

import aiosqlite

from app.storage.base import MemberRepo

_COLS = (
    "id", "member_id", "first_name", "middle_name", "last_name", "gender",
    "date_of_birth", "membership_status", "membership_date", "baptism_date",
    "ministries", "cell_group", "marital_status", "wedding_anniversary",
    "occupation", "employer", "notes", "phone_primary", "phone_secondary",
    "whatsapp", "email", "address_street", "address_city", "country_origin",
    "country_current", "photo_url", "created_at", "updated_at", "created_by",
)


def _row(row) -> dict:
    d = dict(row)
    d["ministries"] = json.loads(d.get("ministries") or "[]")
    return d


def _serialize(doc: dict) -> dict:
    out = dict(doc)
    if "ministries" in out:
        out["ministries"] = json.dumps(out["ministries"])
    return out


class SQLiteMemberRepo(MemberRepo):
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def _next_seq(self) -> int:
        await self._conn.execute(
            "INSERT INTO counters (name, seq) VALUES ('member_seq', 1) "
            "ON CONFLICT(name) DO UPDATE SET seq = seq + 1"
        )
        async with self._conn.execute(
            "SELECT seq FROM counters WHERE name = 'member_seq'"
        ) as cur:
            row = await cur.fetchone()
        return row[0]

    async def get_by_id(self, member_id: str) -> Optional[dict]:
        async with self._conn.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)
        ) as cur:
            row = await cur.fetchone()
        return _row(row) if row else None

    async def get_by_ids(self, ids: List[str]) -> List[dict]:
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        async with self._conn.execute(
            f"SELECT * FROM members WHERE id IN ({placeholders})", ids
        ) as cur:
            rows = await cur.fetchall()
        return [_row(r) for r in rows]

    async def list(
        self,
        q: Optional[str] = None,
        status: Optional[str] = None,
        ministry: Optional[str] = None,
        birthday_month: Optional[int] = None,
        anniversary_month: Optional[int] = None,
        limit: int = 200,
    ) -> List[dict]:
        conditions, params = [], []

        if status:
            conditions.append("membership_status = ?")
            params.append(status)
        if ministry:
            conditions.append(
                "EXISTS (SELECT 1 FROM json_each(ministries) WHERE value = ?)"
            )
            params.append(ministry)
        if q:
            fields = [
                "first_name", "last_name", "middle_name", "member_id",
                "phone_primary", "phone_secondary", "whatsapp", "email",
            ]
            conditions.append("(" + " OR ".join(f"{f} LIKE ?" for f in fields) + ")")
            params.extend([f"%{q}%"] * len(fields))
        if birthday_month:
            conditions.append("date_of_birth != '' AND CAST(substr(date_of_birth, 6, 2) AS INTEGER) = ?")
            params.append(birthday_month)
        if anniversary_month:
            conditions.append(
                "wedding_anniversary IS NOT NULL AND wedding_anniversary != '' "
                "AND CAST(substr(wedding_anniversary, 6, 2) AS INTEGER) = ?"
            )
            params.append(anniversary_month)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM members {where} ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        async with self._conn.execute(sql, params) as cur:
            rows = await cur.fetchall()
        return [_row(r) for r in rows]

    async def create(self, doc: dict) -> dict:
        seq = await self._next_seq()
        doc["member_id"] = f"CHM{seq:05d}"
        s = _serialize(doc)
        placeholders = ",".join("?" * len(_COLS))
        await self._conn.execute(
            f"INSERT INTO members ({','.join(_COLS)}) VALUES ({placeholders})",
            [s.get(c, "") for c in _COLS],
        )
        await self._conn.commit()
        return await self.get_by_id(doc["id"])

    async def update(self, member_id: str, fields: dict) -> Optional[dict]:
        s = _serialize(fields)
        sets = ", ".join(f"{k} = ?" for k in s)
        vals = list(s.values()) + [member_id]
        cur = await self._conn.execute(
            f"UPDATE members SET {sets} WHERE id = ?", vals
        )
        if cur.rowcount == 0:
            await self._conn.rollback()
            return None
        await self._conn.commit()
        return await self.get_by_id(member_id)

    async def deactivate(self, member_id: str, ts: str) -> bool:
        cur = await self._conn.execute(
            "UPDATE members SET membership_status = 'Inactive', updated_at = ? WHERE id = ?",
            (ts, member_id),
        )
        await self._conn.commit()
        return cur.rowcount > 0

    async def count_active(self) -> int:
        async with self._conn.execute(
            "SELECT COUNT(*) FROM members WHERE membership_status = 'Active'"
        ) as cur:
            row = await cur.fetchone()
        return row[0]

    async def count_new_since(self, since_iso: str) -> int:
        async with self._conn.execute(
            "SELECT COUNT(*) FROM members WHERE created_at >= ?", (since_iso,)
        ) as cur:
            row = await cur.fetchone()
        return row[0]

    async def list_non_inactive(self, limit: int = 5000) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM members WHERE membership_status != 'Inactive' LIMIT ?", (limit,)
        ) as cur:
            rows = await cur.fetchall()
        return [_row(r) for r in rows]

    async def list_active(self, limit: int = 5000) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM members WHERE membership_status = 'Active' LIMIT ?", (limit,)
        ) as cur:
            rows = await cur.fetchall()
        return [_row(r) for r in rows]
