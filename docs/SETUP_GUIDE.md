# Church Management System — Setup Guide

## Requirements

- Python 3.11+
- Node.js 18+ and Yarn

---

## Running in development

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt   # or .venv\Scripts\pip on Windows

uvicorn server:app --reload --port 8000
```

The backend starts at **http://localhost:8000**.

### 2. Frontend

Build the React app (output goes to `build/` at the project root):

```bash
cd frontend
yarn install
yarn build
```

Then open **http://localhost:8000** in your browser. Rebuild and refresh after any frontend change.

---

## Default credentials

| Username    | Password   | Role        |
|-------------|------------|-------------|
| superadmin  | Admin@123  | Super Admin |
| admin       | Admin@123  | Admin       |
| staff       | Staff@123  | Staff       |
| viewer      | View@123   | Read-Only   |

Change these passwords before sharing the app on your network.

---

## LAN access

Find this machine's IP address (Windows):

```powershell
ipconfig
```

Look for **IPv4 Address**, e.g. `192.168.1.25`. Other devices on the same network open:

```
http://192.168.1.25:8000
```

Allow port `8000` through Windows Firewall on the host PC.

---

## Configuration

Set these environment variables before starting the backend:

| Variable         | Default       | Description                        |
|------------------|---------------|------------------------------------|
| `DB_PATH`        | `cms.db`      | Path to the SQLite database file   |
| `STATIC_DIR`     | `../build`    | Path to the compiled frontend      |
| `JWT_SECRET`     | auto-random   | Secret key for JWT signing         |
| `ADMIN_PASSWORD` | `Admin@123`   | Password for the `superadmin` user |
