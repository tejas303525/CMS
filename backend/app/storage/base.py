from abc import ABC, abstractmethod
from typing import List, Optional


class UserRepo(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[dict]:
        """Returns the full row including password_hash — for auth use only."""
        ...

    @abstractmethod
    async def list_all(self) -> List[dict]: ...

    @abstractmethod
    async def create(self, doc: dict) -> None: ...

    @abstractmethod
    async def update(self, user_id: str, fields: dict) -> Optional[dict]: ...

    @abstractmethod
    async def delete(self, user_id: str) -> None: ...

    @abstractmethod
    async def touch_login(self, user_id: str, ts: str) -> None: ...


class MemberRepo(ABC):
    @abstractmethod
    async def list(
        self,
        q: Optional[str] = None,
        status: Optional[str] = None,
        ministry: Optional[str] = None,
        birthday_month: Optional[int] = None,
        anniversary_month: Optional[int] = None,
        limit: int = 200,
    ) -> List[dict]: ...

    @abstractmethod
    async def get_by_id(self, member_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def get_by_ids(self, ids: List[str]) -> List[dict]: ...

    @abstractmethod
    async def create(self, doc: dict) -> dict:
        """Generates member_id (CHM{seq:05d}) internally. Returns full doc."""
        ...

    @abstractmethod
    async def update(self, member_id: str, fields: dict) -> Optional[dict]: ...

    @abstractmethod
    async def deactivate(self, member_id: str, ts: str) -> bool: ...

    @abstractmethod
    async def count_active(self) -> int: ...

    @abstractmethod
    async def count_new_since(self, since_iso: str) -> int: ...

    @abstractmethod
    async def list_non_inactive(self, limit: int = 5000) -> List[dict]: ...

    @abstractmethod
    async def list_active(self, limit: int = 5000) -> List[dict]: ...


class FamilyRepo(ABC):
    @abstractmethod
    async def list_all(self) -> List[dict]:
        """Returns families with members: [{member_id, relationship_type}] (not enriched)."""
        ...

    @abstractmethod
    async def get_by_id(self, family_id: str) -> Optional[dict]:
        """Returns family with members: [{member_id, relationship_type}] (not enriched)."""
        ...

    @abstractmethod
    async def create(self, doc: dict) -> dict: ...

    @abstractmethod
    async def update(self, family_id: str, doc: dict) -> Optional[dict]: ...

    @abstractmethod
    async def delete(self, family_id: str) -> None: ...


class ContributionRepo(ABC):
    @abstractmethod
    async def list(
        self,
        member_id: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        contribution_type: Optional[str] = None,
    ) -> List[dict]: ...

    @abstractmethod
    async def get_by_id(self, contribution_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def create(self, doc: dict) -> dict:
        """Generates receipt_no (RCP{seq:06d}) internally. Returns full doc."""
        ...

    @abstractmethod
    async def delete(self, contribution_id: str) -> None: ...

    @abstractmethod
    async def last_by_member(self, member_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def sum_by_month(self, year: int, month: int) -> float: ...

    @abstractmethod
    async def list_by_member_year(self, member_id: str, year: int) -> List[dict]: ...

    @abstractmethod
    async def list_by_month(self, year: int, month: int) -> List[dict]: ...


class AuditRepo(ABC):
    @abstractmethod
    async def insert(self, doc: dict) -> None: ...

    @abstractmethod
    async def list_recent(self, limit: int = 100) -> List[dict]: ...


class Storage(ABC):
    @property
    @abstractmethod
    def users(self) -> UserRepo: ...

    @property
    @abstractmethod
    def members(self) -> MemberRepo: ...

    @property
    @abstractmethod
    def families(self) -> FamilyRepo: ...

    @property
    @abstractmethod
    def contributions(self) -> ContributionRepo: ...

    @property
    @abstractmethod
    def audit(self) -> AuditRepo: ...

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...
