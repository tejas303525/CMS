from typing import Optional

from app.storage.base import Storage

_storage: Optional[Storage] = None


def get_storage() -> Storage:
    return _storage


def set_storage(s: Storage) -> None:
    global _storage
    _storage = s
