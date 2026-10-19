$ErrorActionPreference = "Stop"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "backups\$stamp"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$containerId = (docker compose ps -q mongo).Trim()
if (-not $containerId) {
    throw "mongo container is not running. Start the app first with docker compose up -d"
}

Write-Host "Backing up MongoDB (church) to $backupDir\church-backup.gz ..."
docker exec $containerId mongodump --archive=/tmp/church-backup.gz --gzip --db=church
docker cp "${containerId}:/tmp/church-backup.gz" "$backupDir\church-backup.gz"
docker exec $containerId rm -f /tmp/church-backup.gz

if (Test-Path .env) {
    Copy-Item .env "$backupDir\.env.bak"
}

Write-Host "Backup complete: $backupDir"
Get-ChildItem $backupDir
