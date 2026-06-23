from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

from app.main import app  # noqa: E402 — env must load before app imports

__all__ = ["app"]
