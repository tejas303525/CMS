from fastapi import APIRouter, Depends

from app.auth import require_role
from app.storage.deps import get_storage
from app.storage.base import Storage

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
async def list_audit(
    limit: int = 100,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    return await storage.audit.list_recent(limit=limit)
