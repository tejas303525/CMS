import os
import secrets
import sys
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles


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
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
