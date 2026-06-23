# Church Management System

Full-stack web app for managing church members, families, contributions, and reports. Runs as a single process — FastAPI backend serves both the REST API and the compiled React frontend. Data is stored in a local SQLite file; no external services required.

---

## Stack

| Layer    | Technology                                  |
|----------|---------------------------------------------|
| Backend  | Python 3.11, FastAPI, uvicorn, aiosqlite    |
| Frontend | React 18, shadcn/ui, Tailwind, react-router |
| Storage  | SQLite (WAL mode, via aiosqlite)            |
| Reports  | openpyxl (Excel), reportlab (PDF)           |
| Auth     | JWT (PyJWT), bcrypt                         |

---

## Project layout

```
CMS/
├── backend/
│   ├── server.py               # uvicorn entrypoint
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app, startup, static file serving
│       ├── auth.py             # JWT creation/verification, role guards
│       ├── audit.py            # audit log helper
│       ├── models.py           # Pydantic request/response models
│       ├── routers/            # one file per resource (members, families, …)
│       ├── storage/
│       │   ├── base.py         # abstract Storage interface (ABC)
│       │   ├── deps.py         # get_storage() FastAPI dependency
│       │   └── sqlite/         # SQLite implementation of the interface
│       └── utils/              # pdf.py, excel.py, time.py
├── frontend/
│   └── src/
│       ├── lib/api.js          # axios instance, JWT interceptor
│       ├── lib/auth.jsx        # AuthContext, useAuth hook
│       ├── lib/constants.js    # shared enums, formatters
│       └── pages/             # one file per page
├── build/                      # compiled frontend output (gitignored)
├── tests/
│   └── test_cms_backend.py
└── SETUP_GUIDE.md
```

---

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### Frontend

```bash
cd frontend
yarn install
yarn build                         # outputs to ../build/
```

Open **http://localhost:8000**. Rebuild (`yarn build`) and refresh after frontend changes.

### Default accounts

| Username   | Password  | Role       |
|------------|-----------|------------|
| superadmin | Admin@123 | Super Admin |
| admin      | Admin@123 | Admin      |
| staff      | Staff@123 | Staff      |
| viewer     | View@123  | Read-Only  |

---

## Roles

| Role        | What they can do                                          |
|-------------|-----------------------------------------------------------|
| read_only   | View members, families, dashboard                        |
| staff       | + Create/edit members and families, download reports     |
| admin       | + Record/delete contributions, view finances, audit log  |
| super_admin | + Manage user accounts                                   |

---

## Storage interface

All database access goes through an abstract `Storage` class (`app/storage/base.py`). The SQLite implementation lives in `app/storage/sqlite/`. To swap the backend (e.g. to Postgres), implement the same ABC and pass it to `set_storage()` in `main.py` — routers don't change.

```
Storage
├── .users        → UserRepo
├── .members      → MemberRepo
├── .families     → FamilyRepo
├── .contributions → ContributionRepo
└── .audit        → AuditRepo
```

---

## Environment variables

| Variable         | Default              | Description                              |
|------------------|----------------------|------------------------------------------|
| `DB_PATH`        | `cms.db`             | SQLite file path                         |
| `STATIC_DIR`     | `../build`           | Compiled frontend directory              |
| `JWT_SECRET`     | random on startup    | Sign/verify JWTs — set this in prod      |
| `ADMIN_PASSWORD` | `Admin@123`          | superadmin password (synced on startup)  |
| `ADMIN_USERNAME` | `superadmin`         | superadmin username                      |
| `CORS_ORIGINS`   | `*`                  | Comma-separated allowed origins          |

---

## Running tests

```bash
cd backend
pytest tests/test_cms_backend.py -v
```

Tests spin up a real in-process server with a temporary SQLite database — no mocks.

---

## Reports

Available under `/api/reports/*`. All support `?format=excel` or `?format=pdf`.

| Endpoint                             | Min role | Description                        |
|--------------------------------------|----------|------------------------------------|
| `/reports/members`                   | staff    | Member directory                   |
| `/reports/birthdays?month=N`         | staff    | Birthdays in a given month         |
| `/reports/anniversaries?month=N`     | staff    | Anniversaries in a given month     |
| `/reports/families`                  | staff    | Family list with head and count    |
| `/reports/contributions-monthly`     | admin    | All contributions for a month      |
| `/reports/member-statement/{id}`     | admin    | Annual contribution statement      |
| `/reports/non-contributing?months=N` | admin    | Active members with no recent gift |
