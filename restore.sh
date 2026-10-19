#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: ./restore.sh <path-to-church-backup.gz>" >&2
  exit 1
fi

ARCHIVE="$1"
if [ ! -f "${ARCHIVE}" ]; then
  echo "Backup file not found: ${ARCHIVE}" >&2
  exit 1
fi

CONTAINER_ID=$(docker compose ps -q mongo)
if [ -z "${CONTAINER_ID}" ]; then
  echo "mongo container is not running. Start the app first with docker compose up -d" >&2
  exit 1
fi

echo "This will REPLACE the current 'church' database with the contents of ${ARCHIVE}."
read -r -p "Type 'yes' to continue: " CONFIRM
if [ "${CONFIRM}" != "yes" ]; then
  echo "Aborted."
  exit 1
fi

docker cp "${ARCHIVE}" "${CONTAINER_ID}:/tmp/restore.gz"
docker exec "${CONTAINER_ID}" mongorestore --archive=/tmp/restore.gz --gzip --drop
docker exec "${CONTAINER_ID}" rm -f /tmp/restore.gz

echo "Restore complete from ${ARCHIVE}"
