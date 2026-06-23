import aiosqlite

from app.storage.base import Storage, UserRepo, MemberRepo, FamilyRepo, ContributionRepo, AuditRepo
from app.storage.sqlite.users import SQLiteUserRepo
from app.storage.sqlite.members import SQLiteMemberRepo
from app.storage.sqlite.families import SQLiteFamilyRepo
from app.storage.sqlite.contributions import SQLiteContributionRepo
from app.storage.sqlite.audit import SQLiteAuditRepo

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name    TEXT NOT NULL,
    role         TEXT NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 1,
    last_login   TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    id                 TEXT PRIMARY KEY,
    member_id          TEXT UNIQUE NOT NULL,
    first_name         TEXT NOT NULL DEFAULT '',
    middle_name        TEXT NOT NULL DEFAULT '',
    last_name          TEXT NOT NULL DEFAULT '',
    gender             TEXT NOT NULL DEFAULT '',
    date_of_birth      TEXT NOT NULL DEFAULT '',
    membership_status  TEXT NOT NULL DEFAULT 'Active',
    membership_date    TEXT,
    baptism_date       TEXT,
    ministries         TEXT NOT NULL DEFAULT '[]',
    cell_group         TEXT NOT NULL DEFAULT '',
    marital_status     TEXT NOT NULL DEFAULT 'Single',
    wedding_anniversary TEXT,
    occupation         TEXT NOT NULL DEFAULT '',
    employer           TEXT NOT NULL DEFAULT '',
    notes              TEXT NOT NULL DEFAULT '',
    phone_primary      TEXT NOT NULL DEFAULT '',
    phone_secondary    TEXT NOT NULL DEFAULT '',
    whatsapp           TEXT NOT NULL DEFAULT '',
    email              TEXT NOT NULL DEFAULT '',
    address_street     TEXT NOT NULL DEFAULT '',
    address_city       TEXT NOT NULL DEFAULT '',
    country_origin     TEXT NOT NULL DEFAULT '',
    country_current    TEXT NOT NULL DEFAULT '',
    photo_url          TEXT NOT NULL DEFAULT '',
    created_at         TEXT NOT NULL,
    updated_at         TEXT NOT NULL,
    created_by         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS families (
    id             TEXT PRIMARY KEY,
    family_name    TEXT NOT NULL,
    head_member_id TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    updated_at     TEXT,
    created_by     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS family_members (
    family_id         TEXT NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    member_id         TEXT NOT NULL,
    relationship_type TEXT NOT NULL DEFAULT 'Other',
    PRIMARY KEY (family_id, member_id)
);

CREATE TABLE IF NOT EXISTS contributions (
    id               TEXT PRIMARY KEY,
    member_id        TEXT NOT NULL,
    contribution_date TEXT NOT NULL,
    contribution_type TEXT NOT NULL,
    amount           REAL NOT NULL,
    payment_mode     TEXT NOT NULL,
    reference_no     TEXT NOT NULL DEFAULT '',
    notes            TEXT NOT NULL DEFAULT '',
    receipt_no       TEXT UNIQUE NOT NULL,
    currency         TEXT NOT NULL DEFAULT 'INR',
    year             INTEGER NOT NULL,
    month            INTEGER NOT NULL,
    member_name      TEXT NOT NULL,
    member_external_id TEXT NOT NULL,
    recorded_by      TEXT NOT NULL,
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL,
    username   TEXT NOT NULL,
    action     TEXT NOT NULL,
    entity     TEXT NOT NULL,
    entity_id  TEXT NOT NULL,
    details    TEXT NOT NULL DEFAULT '{}',
    timestamp  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS counters (
    name TEXT PRIMARY KEY,
    seq  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_members_status  ON members(membership_status);
CREATE INDEX IF NOT EXISTS idx_members_created ON members(created_at);
CREATE INDEX IF NOT EXISTS idx_contrib_member  ON contributions(member_id, contribution_date);
CREATE INDEX IF NOT EXISTS idx_contrib_ym      ON contributions(year, month);
CREATE INDEX IF NOT EXISTS idx_audit_ts        ON audit_logs(timestamp);
"""


class SQLiteStorage(Storage):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn: aiosqlite.Connection = None
        self._users: SQLiteUserRepo = None
        self._members: SQLiteMemberRepo = None
        self._families: SQLiteFamilyRepo = None
        self._contributions: SQLiteContributionRepo = None
        self._audit: SQLiteAuditRepo = None

    @property
    def users(self) -> UserRepo:
        return self._users

    @property
    def members(self) -> MemberRepo:
        return self._members

    @property
    def families(self) -> FamilyRepo:
        return self._families

    @property
    def contributions(self) -> ContributionRepo:
        return self._contributions

    @property
    def audit(self) -> AuditRepo:
        return self._audit

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._conn.executescript(_SCHEMA)
        self._users = SQLiteUserRepo(self._conn)
        self._members = SQLiteMemberRepo(self._conn)
        self._families = SQLiteFamilyRepo(self._conn)
        self._contributions = SQLiteContributionRepo(self._conn)
        self._audit = SQLiteAuditRepo(self._conn)

    async def disconnect(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None
