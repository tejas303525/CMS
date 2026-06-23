from collections import defaultdict
from typing import List, Optional

import aiosqlite

from app.storage.base import FamilyRepo


class SQLiteFamilyRepo(FamilyRepo):
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    def _attach_members(self, families: List[dict], member_rows) -> None:
        by_family: dict = defaultdict(list)
        for r in member_rows:
            by_family[r["family_id"]].append(
                {"member_id": r["member_id"], "relationship_type": r["relationship_type"]}
            )
        for f in families:
            f["members"] = by_family.get(f["id"], [])

    async def list_all(self) -> List[dict]:
        async with self._conn.execute(
            "SELECT * FROM families ORDER BY created_at DESC LIMIT 500"
        ) as cur:
            fam_rows = await cur.fetchall()

        families = [dict(r) for r in fam_rows]
        if not families:
            return families

        ids = [f["id"] for f in families]
        placeholders = ",".join("?" * len(ids))
        async with self._conn.execute(
            f"SELECT family_id, member_id, relationship_type FROM family_members WHERE family_id IN ({placeholders})",
            ids,
        ) as cur:
            mem_rows = await cur.fetchall()

        self._attach_members(families, mem_rows)
        return families

    async def get_by_id(self, family_id: str) -> Optional[dict]:
        async with self._conn.execute(
            "SELECT * FROM families WHERE id = ?", (family_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        fam = dict(row)
        async with self._conn.execute(
            "SELECT member_id, relationship_type FROM family_members WHERE family_id = ?",
            (family_id,),
        ) as cur:
            mem_rows = await cur.fetchall()
        fam["members"] = [
            {"member_id": r["member_id"], "relationship_type": r["relationship_type"]}
            for r in mem_rows
        ]
        return fam

    async def create(self, doc: dict) -> dict:
        members = doc.get("members", [])
        await self._conn.execute(
            "INSERT INTO families (id, family_name, head_member_id, created_at, created_by) VALUES (?, ?, ?, ?, ?)",
            (doc["id"], doc["family_name"], doc["head_member_id"], doc["created_at"], doc["created_by"]),
        )
        if members:
            await self._conn.executemany(
                "INSERT INTO family_members (family_id, member_id, relationship_type) VALUES (?, ?, ?)",
                [(doc["id"], m["member_id"], m.get("relationship_type", "Other")) for m in members],
            )
        await self._conn.commit()
        return await self.get_by_id(doc["id"])

    async def update(self, family_id: str, doc: dict) -> Optional[dict]:
        members = doc.get("members", [])
        cur = await self._conn.execute(
            "UPDATE families SET family_name = ?, head_member_id = ?, updated_at = ? WHERE id = ?",
            (doc["family_name"], doc["head_member_id"], doc.get("updated_at"), family_id),
        )
        if cur.rowcount == 0:
            await self._conn.rollback()
            return None
        await self._conn.execute(
            "DELETE FROM family_members WHERE family_id = ?", (family_id,)
        )
        if members:
            await self._conn.executemany(
                "INSERT INTO family_members (family_id, member_id, relationship_type) VALUES (?, ?, ?)",
                [(family_id, m["member_id"], m.get("relationship_type", "Other")) for m in members],
            )
        await self._conn.commit()
        return await self.get_by_id(family_id)

    async def delete(self, family_id: str) -> None:
        await self._conn.execute("DELETE FROM families WHERE id = ?", (family_id,))
        await self._conn.commit()
