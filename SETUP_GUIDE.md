# CMS Setup Guide

This guide sets up the Church Management System on a Windows machine for local or LAN-only use.

## 1. Required Tools

Install these first:

- Python 3.11
- Node.js LTS
- MongoDB Community Server
- MongoDB Compass
- Git, optional
- Visual Studio Code, optional

Recommended Python version:

```powershell
py -3.11 --version
```

Do not use Python 3.14 for this project. Some backend packages do not support it yet.

## 2. Project Folder

Open PowerShell and go to the project:

```powershell
cd C:\Users\IT\Desktop\CMS\CMS
```

If your project is in another location, use that path instead.

## 3. MongoDB Setup

Open MongoDB Compass.

Create:

```text
Database Name: church
Collection Name: users
```

Do not enable Time-Series.

The app will create/use other collections automatically:

```text
members
contributions
families
audit_logs
```

For local use, MongoDB should run at:

```text
mongodb://localhost:27017
```

## 4. Backend Environment File

Create this file:

```text
C:\Users\IT\Desktop\CMS\CMS\backend\.env
```

Paste:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=church
JWT_SECRET=change-this-to-a-long-random-secret
CORS_ORIGINS=http://localhost:3000
```

To generate a random JWT secret in PowerShell:

```powershell
$bytes = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); [Convert]::ToBase64String($bytes)
```

For LAN access, replace `CORS_ORIGINS` with your PC IP:

```env
CORS_ORIGINS=http://192.168.1.25:3000
```

## 5. Frontend Environment File

Create this file:

```text
C:\Users\IT\Desktop\CMS\CMS\frontend\.env
```

For local use, paste:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

For LAN access, use your PC IP:

```env
REACT_APP_BACKEND_URL=http://192.168.1.25:8001
```

## 6. Backend Setup

Open PowerShell:

```powershell
cd C:\Users\IT\Desktop\CMS\CMS\backend
```

Create a Python 3.11 virtual environment:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\activate
```

Confirm Python version:

```powershell
python --version
```

It should show Python 3.11.x.

Install dependencies:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Run backend:

```powershell
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Check API:

```text
http://localhost:8001/api/
```

API docs:

```text
http://localhost:8001/docs
```

## 7. Frontend Setup

Open a second PowerShell terminal:

```powershell
cd C:\Users\IT\Desktop\CMS\CMS\frontend
```

Install dependencies:

```powershell
npm install
```

If npm reports dependency conflicts, run:

```powershell
npm install --legacy-peer-deps
```

Run frontend:

```powershell
npm start
```

Open:

```text
http://localhost:3000
```

## 8. Default Login

The app seeds these users on startup:

```text
superadmin / Admin@123
admin      / Admin@123
staff      / Staff@123
viewer     / View@123
```

Important: change these passwords before sharing the app on your network.

## 9. LAN Access

Find your PC IP:

```powershell
ipconfig
```

Look for IPv4 Address, for example:

```text
192.168.1.25
```

Backend should run with:

```powershell
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Frontend can run with:

```powershell
$env:HOST="0.0.0.0"
npm start
```

Other users on the same network open:

```text
http://192.168.1.25:3000
```

Allow these Windows Firewall inbound ports on the host PC:

```text
3000
8001
```

Do not expose MongoDB port `27017` unless the database must be accessed from another machine.

## 10. Common Problems

### Python shows 3.14

Delete wrong virtual environments and recreate with Python 3.11:

```powershell
deactivate
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python --version
```

### PowerShell blocks venv activation

Run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then:

```powershell
.\.venv\Scripts\activate
```

### Login gives 404

Check frontend `.env`:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

Restart frontend after changing `.env`:

```powershell
Ctrl + C
npm start
```

### npm says craco is not recognized

Dependencies were not installed. Run:

```powershell
cd C:\Users\IT\Desktop\CMS\CMS\frontend
npm install
npm start
```

### requirements.txt install fails with grpc conflict

You are probably using Python 3.14. Use Python 3.11.

### Backend cannot connect to database

Check MongoDB service is running and `.env` has:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=church
```

## 11. Quick Start Commands

Backend:

```powershell
cd C:\Users\IT\Desktop\CMS\CMS\backend
.\.venv\Scripts\activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Frontend:

```powershell
cd C:\Users\IT\Desktop\CMS\CMS\frontend
npm start
```

Open:

```text
http://localhost:3000
```
