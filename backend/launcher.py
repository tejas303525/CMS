import os
import secrets
import sys
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


class SPAStaticFiles(StaticFiles):
    """Serve the React build, falling back to index.html for unknown paths.

    The compiled frontend uses client-side routing (React Router), so a
    direct browser navigation or hard refresh on a route like /login or
    /members has no matching file on disk. Without this fallback, that
    lands on this StaticFiles mount and 404s instead of loading the app,
    which then bootstraps the client router itself.
    """

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


def runtime_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent / "target" / "windows"


base_dir = runtime_dir()
secret_file = base_dir / ".jwt_secret"
if not secret_file.exists():
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    secret_file.write_text(secrets.token_urlsafe(48), encoding="utf-8")

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "church")
os.environ.setdefault("JWT_SECRET", secret_file.read_text(encoding="utf-8").strip())

from server import app  # noqa: E402

build_dir = base_dir / "build"
if build_dir.exists():
    app.mount("/", SPAStaticFiles(directory=str(build_dir), html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
