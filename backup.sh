#!/usr/bin/env bash
set -euo pipefail

STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="backups/${STAMP}"
mkdir -p "${BACKUP_DIR}"

CONTAINER_ID=$(docker compose ps -q mongo)
if [ -z "${CONTAINER_ID}" ]; then
  echo "mongo container is not running. Start the app first with docker compose up -d" >&2
  exit 1
fi

echo "Backing up MongoDB (church) to ${BACKUP_DIR}/church-backup.gz ..."
docker exec "${CONTAINER_ID}" mongodump --archive=/tmp/church-backup.gz --gzip --db=church
docker cp "${CONTAINER_ID}:/tmp/church-backup.gz" "${BACKUP_DIR}/church-backup.gz"
docker exec "${CONTAINER_ID}" rm -f /tmp/church-backup.gz

if [ -f .env ]; then
  cp .env "${BACKUP_DIR}/.env.bak"
fi

echo "Backup complete: ${BACKUP_DIR}"
ls -lh "${BACKUP_DIR}"
