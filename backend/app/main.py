import os
import logging
import uuid
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from app.auth import init_auth, hash_password, verify_password
from app.storage.sqlite.impl import SQLiteStorage
from app.storage.deps import set_storage
from app.utils.time import now_utc
from app.routers import auth, users, members, families, contributions, dashboard, reports, audit_logs

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("cms")

app = FastAPI(title="Church Management System")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    auth.router, users.router, members.router, families.router,
    contributions.router, dashboard.router, reports.router, audit_logs.router,
]:
    app.include_router(router, prefix="/api")


@app.get("/api/")
async def root():
    return {"app": "Church Management System", "version": "1.0"}


# Serve the React SPA — must be registered after all API routes.
# STATIC_DIR can be overridden at runtime (useful for PyInstaller bundle).
_static = Path(os.environ.get("STATIC_DIR", Path(__file__).parent.parent.parent / "build"))

if _static.exists():
    app.mount("/static", StaticFiles(directory=_static / "static"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        return FileResponse(_static / "index.html")
else:
    log.warning("Frontend build not found at %s — serving API only. Run 'yarn build' in frontend/.", _static)


_storage: SQLiteStorage = None


@app.on_event("startup")
async def startup():
    global _storage
    init_auth()

    db_path = os.environ.get("DB_PATH", "cms.db")
    _storage = SQLiteStorage(db_path)
    await _storage.connect()
    set_storage(_storage)

    admin_username = os.environ.get("ADMIN_USERNAME", "superadmin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123")

    existing = await _storage.users.get_by_username(admin_username)
    if not existing:
        await _storage.users.create({
            "id": str(uuid.uuid4()),
            "username": admin_username,
            "password_hash": hash_password(admin_password),
            "full_name": "Super Administrator",
            "role": "super_admin",
            "is_active": True,
            "last_login": None,
            "created_at": now_utc().isoformat(),
        })
        log.info(f"Seeded super admin: {admin_username}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await _storage.users.update(existing["id"], {"password_hash": hash_password(admin_password)})

    for u in [
        {"username": "admin",  "password": "Admin@123", "full_name": "Church Admin",    "role": "admin"},
        {"username": "staff",  "password": "Staff@123", "full_name": "Ministry Leader", "role": "staff"},
        {"username": "viewer", "password": "View@123",  "full_name": "Cell Leader",     "role": "read_only"},
    ]:
        if not await _storage.users.get_by_username(u["username"]):
            await _storage.users.create({
                "id": str(uuid.uuid4()),
                "username": u["username"],
                "password_hash": hash_password(u["password"]),
                "full_name": u["full_name"],
                "role": u["role"],
                "is_active": True,
                "last_login": None,
                "created_at": now_utc().isoformat(),
            })


@app.on_event("shutdown")
async def shutdown():
    if _storage:
        await _storage.disconnect()
