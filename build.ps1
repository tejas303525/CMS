$ErrorActionPreference = "Stop"

$BACKEND_VERSION = (Get-Content backend\version.txt).Trim()
$FRONTEND_VERSION = (Get-Content frontend\package.json | ConvertFrom-Json).version

Write-Host "Building backend  v$BACKEND_VERSION"
docker build -t "cms-backend:$BACKEND_VERSION" .\backend

Write-Host "Building frontend v$FRONTEND_VERSION"
docker build -t "cms-frontend:$FRONTEND_VERSION" .\frontend

Write-Host "Done."
Write-Host "  cms-backend:$BACKEND_VERSION"
Write-Host "  cms-frontend:$FRONTEND_VERSION"
