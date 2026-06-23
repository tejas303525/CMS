from typing import List, Optional

import aiosqlite

from app.storage.base import ContributionRepo

_COLS = (
    "id", "member_id", "contribution_date", "contribution_type", "amount",
    "payment_mode", "reference_no", "notes", "receipt_no", "currency",
    "year", "month", "member_name", "member_external_id", "recorded_by", "created_at",
)


class SQLiteContributionRepo(ContributionRepo):
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def _next_seq(self) -> int:
        await self._conn.execute(
            "INSERT INTO counters (name, seq) VALUES ('receipt_seq', 1) "
            "ON CONFLICT(name) DO UPDATE SET seq = seq + 1"
        )
        async with self._conn.execute(
            "SELECT seq FROM counters WHERE name = 'receipt_seq'"
        ) as cur:
            row = await cur.fetchone()
        return row[0]

    async def list(
        self,
        member_id: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        contribution_type: Optional[str] = None,
    ) -> List[dict]:
        conditions, params = [], []
        if member_id:
            conditions.append("member_id = ?"); params.append(member_id)
        if year:
            conditions.append("year = ?"); params.append(year)
        if month:
            conditions.append("month = ?"); params.append(month)
        if contribution_type:
            conditions.append("contribution_type = ?"); params.append(contribution_type)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        async with self._conn.execute(
            f"SELECT * FROM contributions {where} ORDER BY contribution_date DESC LIMIT 1000", params
        ) as cur:
            rows = await cur.fetchall()
        return [dict(r) for r in rows]

    async def get_by_id(self, contribution_id: str) -> Optional[dict]:
        async with self._conn.execute(
            "SELECT * FROM contributions WHERE id = ?", (contribution_id,)
        ) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None

    async def create(self, doc: dict) -> dict:
        seq = await self._next_seq()
        doc["receipt_no"] = f"RCP{seq:06d}"
        await self._conn.execute(
            f"INSERT INTO contributions ({','.join(_COLS)}) VALUES ({','.join('?' * len(_COLS))})",
            [doc.get(c) for c in _COLS],
        )
        await self._conn.commit()
        return await self.get_by_id(doc["id"])

    async def delete(self, contribution_id: str) -> None:
        await self._conn.execute(
            "DELETE FROM contributions WHERE id = ?", (contribution_id,)
        )
        await self._conn.commit()

    async def last_by_member(self, member_id: str) -> Optional[dict]:
        async with self._conn.execute(
            "SELECT * FROM contributions WHERE member_id = ? ORDER BY contribution_date DESC LIMIT 1",
            (member_id,),
        ) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None

    async def sum_by_month(self, year: int, month: int) -> float:
        async with self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM contributions WHERE year = ? AND month = ?",
            (year, month),
        ) as cur:
            row = await cur.fetchone()
        return float(row[0])

    async def list_by_member_year(self, member_id: str, year: int) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM contributions WHERE member_id = ? AND year = ? ORDER BY contribution_date",
            (member_id, year),
        ) as cur:
            rows = await cur.fetchall()
        return [dict(r) for r in rows]

    async def list_by_month(self, year: int, month: int) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM contributions WHERE year = ? AND month = ? ORDER BY contribution_date",
            (year, month),
        ) as cur:
            rows = await cur.fetchall()
        return [dict(r) for r in rows]
