import uuid
from typing import Optional

from app.utils.time import now_utc


async def audit(
    storage,
    user: dict,
    action: str,
    entity: str,
    entity_id: str,
    details: Optional[dict] = None,
) -> None:
    await storage.audit.insert({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "username": user["username"],
        "action": action,
        "entity": entity,
        "entity_id": entity_id,
        "details": details or {},
        "timestamp": now_utc().isoformat(),
    })
