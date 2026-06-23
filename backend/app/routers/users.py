import uuid
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from app.auth import require_role, hash_password
from app.audit import audit
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.models import UserPublic, UserCreateIn, UserUpdateIn
from app.utils.time import now_utc

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserPublic])
async def list_users(
    _: dict = Depends(require_role("super_admin")),
    storage: Storage = Depends(get_storage),
):
    return await storage.users.list_all()


@router.post("", response_model=UserPublic)
async def create_user(
    body: UserCreateIn,
    user: dict = Depends(require_role("super_admin")),
    storage: Storage = Depends(get_storage),
):
    if await storage.users.get_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    doc = {
        "id": str(uuid.uuid4()),
        "username": body.username,
        "password_hash": hash_password(body.password),
        "full_name": body.full_name,
        "role": body.role,
        "is_active": True,
        "last_login": None,
        "created_at": now_utc().isoformat(),
    }
    await storage.users.create(doc)
    await audit(storage, user, "create", "user", doc["id"], {"username": body.username, "role": body.role})
    doc.pop("password_hash", None)
    return doc


@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: str,
    body: UserUpdateIn,
    user: dict = Depends(require_role("super_admin")),
    storage: Storage = Depends(get_storage),
):
    fields = {}
    if body.full_name is not None: fields["full_name"] = body.full_name
    if body.role is not None: fields["role"] = body.role
    if body.is_active is not None: fields["is_active"] = body.is_active
    if body.password: fields["password_hash"] = hash_password(body.password)
    doc = await storage.users.update(user_id, fields)
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    await audit(storage, user, "update", "user", user_id, {"fields": list(fields.keys())})
    return doc


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user: dict = Depends(require_role("super_admin")),
    storage: Storage = Depends(get_storage),
):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    await storage.users.delete(user_id)
    await audit(storage, user, "delete", "user", user_id)
    return {"ok": True}
