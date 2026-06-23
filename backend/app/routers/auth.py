from fastapi import APIRouter, HTTPException, Depends

from app.auth import get_current_user, create_access_token, verify_password
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.models import LoginIn
from app.utils.time import now_utc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(body: LoginIn, storage: Storage = Depends(get_storage)):
    user = await storage.users.get_by_username(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")
    token = create_access_token(user["id"], user["username"], user["role"])
    await storage.users.touch_login(user["id"], now_utc().isoformat())
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "is_active": user["is_active"],
        },
    }


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user
