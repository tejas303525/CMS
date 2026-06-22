# CMS Setup Guide

This guide sets up the Church Management System on a Windows machine using Docker.

## 1. Install Docker Desktop

Download and install Docker Desktop for Windows:

```text
https://www.docker.com/products/docker-desktop
```

After installing, open Docker Desktop and wait until the status bar at the bottom shows **"Engine running"**.

Verify in PowerShell:

```powershell
docker --version
docker compose version
```

## 2. Project Folder

Open PowerShell and go to the project:

```powershell
cd C:\Users\IT\Desktop\CMS
```

If your project is in another location, use that path instead.

## 3. Environment File

Create a file named `.env` in the project root folder:

```powershell
notepad .env
```

Paste the following and save:

```env
JWT_SECRET=change-this-to-a-long-random-secret
```

To generate a proper random secret, run this in PowerShell and copy the output into the `.env` file:

```powershell
$bytes = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); [Convert]::ToBase64String($bytes)
```

## 4. Build the Docker Images

In PowerShell, from the project root:

```powershell
.\build.ps1
```

If PowerShell blocks the script, run this once and then retry:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

The build will take several minutes the first time. You will see Docker downloading base images and installing dependencies. Subsequent builds are much faster.

When finished you should see:

```text
Done.
  cms-backend:0.0.1
  cms-frontend:0.1.0
```

## 5. Start the App

```powershell
docker compose up -d
```

This starts MongoDB, the backend, and the frontend. Open the app in a browser:

```text
http://localhost:3000
```

To stop the app:

```powershell
docker compose down
```

## 6. Default Login

The app creates these accounts on first startup:

```text
superadmin / Admin@123
admin      / Admin@123
staff      / Staff@123
viewer     / View@123
```

Change these passwords before sharing the app on your network.

## 7. LAN Access

To let other computers on the same network use the app, find this machine's IP address:

```powershell
ipconfig
```

Look for **IPv4 Address**, for example `192.168.1.25`. Other users open:

```text
http://192.168.1.25:3000
```

Allow these ports through Windows Firewall on the host PC:

```text
3000   (app)
8001   (backend API)
```

Do not expose port `27017`.

## 8. Upgrading

After any code change, rebuild the images and restart:

```powershell
.\build.ps1
docker compose down
docker compose up -d
```

## 9. Common Problems

### Docker Desktop not starting

Make sure virtualisation is enabled in your PC's BIOS. On Windows 11 it is usually on by default. If Docker Desktop still fails to start, enable WSL 2 by running in PowerShell as Administrator:

```powershell
wsl --install
```

Then restart the PC and open Docker Desktop again.

### build.ps1 is blocked by PowerShell

Run once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### App not loading at localhost:3000

Check that all three containers are running:

```powershell
docker compose ps
```

View logs if something is wrong:

```powershell
docker compose logs frontend
docker compose logs backend
```

### Login fails or shows an error

Check that `.env` exists in the project root and contains `JWT_SECRET`. Then restart:

```powershell
docker compose down
docker compose up -d
```

### Data is lost after restarting

This should not happen. Data is stored in a Docker volume that persists across restarts. If you ran `docker compose down -v`, the volume was deleted. This is only needed when you want to wipe everything and start fresh.

## 10. Quick Start (after first setup)

```powershell
cd C:\Users\IT\Desktop\CMS
docker compose up -d
```

Open `http://localhost:3000`.
