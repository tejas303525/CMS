import uuid
from fastapi import APIRouter, HTTPException, Depends

from app.auth import get_current_user, require_role
from app.audit import audit
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.models import FamilyIn
from app.utils.time import now_utc

router = APIRouter(prefix="/families", tags=["families"])


@router.get("")
async def list_families(
    user: dict = Depends(get_current_user),
    storage: Storage = Depends(get_storage),
):
    return await storage.families.list_all()


@router.post("")
async def create_family(
    body: FamilyIn,
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_utc().isoformat()
    doc["created_by"] = user["username"]
    created = await storage.families.create(doc)
    await audit(storage, user, "create", "family", created["id"])
    return created


@router.get("/{family_id}")
async def get_family(
    family_id: str,
    user: dict = Depends(get_current_user),
    storage: Storage = Depends(get_storage),
):
    fam = await storage.families.get_by_id(family_id)
    if not fam:
        raise HTTPException(status_code=404, detail="Family not found")

    ids = [fam["head_member_id"]] + [m["member_id"] for m in fam.get("members", [])]
    members = await storage.members.get_by_ids(ids)
    members_by_id = {m["id"]: m for m in members}

    fam["head_member"] = members_by_id.get(fam["head_member_id"])
    fam["enriched_members"] = [
        {**members_by_id[m["member_id"]], "relationship_type": m.get("relationship_type", "Other")}
        for m in fam.get("members", [])
        if m["member_id"] in members_by_id
    ]
    return fam


@router.patch("/{family_id}")
async def update_family(
    family_id: str,
    body: FamilyIn,
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    doc = body.model_dump()
    doc["updated_at"] = now_utc().isoformat()
    updated = await storage.families.update(family_id, doc)
    if not updated:
        raise HTTPException(status_code=404, detail="Family not found")
    await audit(storage, user, "update", "family", family_id)
    return updated


@router.delete("/{family_id}")
async def delete_family(
    family_id: str,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    await storage.families.delete(family_id)
    await audit(storage, user, "delete", "family", family_id)
    return {"ok": True}
