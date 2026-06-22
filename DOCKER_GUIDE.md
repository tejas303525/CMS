# Docker Guide

Reference for day-to-day Docker operations on this project.

## Workflow overview

```text
build.ps1  →  docker compose up -d  →  app at localhost:3000
```

Images are built once with `build.ps1` and reused by `docker compose`. You do not need to rebuild unless the code changes.

---

## Daily use

### Start the app

```powershell
docker compose up -d
```

### Stop the app

```powershell
docker compose down
```

### Restart the app

```powershell
docker compose down
docker compose up -d
```

---

## Building images

Run from the project root after any code change:

```powershell
.\build.ps1
```

Then restart:

```powershell
docker compose down
docker compose up -d
```

The image tags come from:

| Image | Version source |
|---|---|
| `cms-backend` | `backend\version.txt` |
| `cms-frontend` | `frontend\package.json` |

To run a specific version without rebuilding:

```powershell
$env:BACKEND_VERSION="0.0.1"; $env:FRONTEND_VERSION="0.1.0"; docker compose up -d
```

---

## Viewing logs

All containers:

```powershell
docker compose logs -f
```

One container at a time:

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mongo
```

Press `Ctrl+C` to stop following logs.

---

## Container status

```powershell
docker compose ps
```

All three services should show `running`.

---

## Data

MongoDB data is stored in a Docker volume called `mongo_data`. It persists across `down` and `up` cycles.

To wipe all data and start fresh:

```powershell
docker compose down -v
docker compose up -d
```

---

## Moving to another Windows PC

### Option A — Rebuild on the new PC (recommended)

1. Copy the entire project folder to the new PC.
2. Install Docker Desktop.
3. Open PowerShell in the project folder and run:

```powershell
.\build.ps1
docker compose up -d
```

### Option B — Transfer the images (no internet needed on target PC)

On the source PC, export the images:

```powershell
docker save cms-backend:0.0.1 cms-frontend:0.1.0 -o cms-images.tar
```

Copy `cms-images.tar` and the project folder to the new PC, then import:

```powershell
docker load -i cms-images.tar
docker compose up -d
```

---

## Ports

| Port | Service |
|---|---|
| `3000` | Frontend (open this in the browser) |
| `8001` | Backend API |
| `27017` | MongoDB (do not expose outside the PC) |

---

## Common commands reference

| Task | Command |
|---|---|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| Rebuild images | `.\build.ps1` |
| View logs | `docker compose logs -f` |
| Check status | `docker compose ps` |
| Wipe data | `docker compose down -v` |
| List local images | `docker images` |
