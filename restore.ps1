param(
    [Parameter(Mandatory = $true)][string]$ArchivePath
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path $ArchivePath)) {
    throw "Backup file not found: $ArchivePath"
}

$containerId = (docker compose ps -q mongo).Trim()
if (-not $containerId) {
    throw "mongo container is not running. Start the app first with docker compose up -d"
}

Write-Host "This will REPLACE the current 'church' database with the contents of $ArchivePath."
$confirm = Read-Host "Type 'yes' to continue"
if ($confirm -ne "yes") {
    Write-Host "Aborted."
    exit 1
}

docker cp $ArchivePath "${containerId}:/tmp/restore.gz"
docker exec $containerId mongorestore --archive=/tmp/restore.gz --gzip --drop
docker exec $containerId rm -f /tmp/restore.gz

Write-Host "Restore complete from $ArchivePath"
