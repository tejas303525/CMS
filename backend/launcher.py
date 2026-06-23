"""
PyInstaller entry point.

Run directly in dev:   python launcher.py
Run as frozen exe:     cms.exe  (PyInstaller --onefile)
"""
import sys
import os
from pathlib import Path

# ── Frozen-mode path setup (must happen before any app imports) ────────────────
if getattr(sys, "frozen", False):
    _exe_dir = Path(sys.executable).parent
    os.environ.setdefault("STATIC_DIR", str(_exe_dir / "build"))
    os.environ.setdefault("DB_PATH",    str(_exe_dir / "cms.db"))
    _dotenv   = _exe_dir / ".env"
    _key_file = _exe_dir / ".jwt_secret"
else:
    _here     = Path(__file__).parent
    _dotenv   = _here / ".env"
    _key_file = _here / ".jwt_secret"

# ── Load .env (optional — church IT can drop one next to the exe) ──────────────
from dotenv import load_dotenv
load_dotenv(_dotenv)

# ── JWT_SECRET: use env/dotenv value, or generate-and-persist one ─────────────
if "JWT_SECRET" not in os.environ:
    if _key_file.exists():
        os.environ["JWT_SECRET"] = _key_file.read_text().strip()
    else:
        import secrets
        _secret = secrets.token_hex(32)
        _key_file.write_text(_secret)
        os.environ["JWT_SECRET"] = _secret

# ── Import app (env vars are all set now) ─────────────────────────────────────
from app.main import app  # noqa: E402
import uvicorn             # noqa: E402

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()   # required for PyInstaller --onefile on Windows

    port = int(os.environ.get("PORT", 8000))
    print(f"CMS starting on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
