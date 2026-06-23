import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from app.auth import get_current_user, require_role
from app.audit import audit
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.models import MemberIn, ROLE_LEVEL
from app.utils.time import now_utc

router = APIRouter(prefix="/members", tags=["members"])


@router.get("")
async def list_members(
    q: Optional[str] = None,
    status: Optional[str] = None,
    ministry: Optional[str] = None,
    birthday_month: Optional[int] = None,
    anniversary_month: Optional[int] = None,
    limit: int = 200,
    user: dict = Depends(get_current_user),
    storage: Storage = Depends(get_storage),
):
    return await storage.members.list(
        q=q, status=status, ministry=ministry,
        birthday_month=birthday_month, anniversary_month=anniversary_month,
        limit=limit,
    )


@router.post("")
async def create_member(
    body: MemberIn,
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_utc().isoformat()
    doc["updated_at"] = doc["created_at"]
    doc["created_by"] = user["username"]
    created = await storage.members.create(doc)
    await audit(storage, user, "create", "member", created["id"], {"member_id": created["member_id"]})
    return created


@router.get("/{member_id}")
async def get_member(
    member_id: str,
    user: dict = Depends(get_current_user),
    storage: Storage = Depends(get_storage),
):
    doc = await storage.members.get_by_id(member_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Member not found")
    if ROLE_LEVEL.get(user["role"], 0) < ROLE_LEVEL["admin"]:
        doc["notes"] = ""
    return doc


@router.patch("/{member_id}")
async def update_member(
    member_id: str,
    body: MemberIn,
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    fields = body.model_dump()
    fields["updated_at"] = now_utc().isoformat()
    doc = await storage.members.update(member_id, fields)
    if not doc:
        raise HTTPException(status_code=404, detail="Member not found")
    await audit(storage, user, "update", "member", member_id)
    return doc


@router.delete("/{member_id}")
async def soft_delete_member(
    member_id: str,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    found = await storage.members.deactivate(member_id, now_utc().isoformat())
    if not found:
        raise HTTPException(status_code=404, detail="Member not found")
    await audit(storage, user, "deactivate", "member", member_id)
    return {"ok": True}
