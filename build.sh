#!/usr/bin/env bash
set -euo pipefail

BACKEND_VERSION=$(cat backend/version.txt | tr -d '[:space:]')
FRONTEND_VERSION=$(grep '"version"' frontend/package.json | sed 's/.*"version":[[:space:]]*"\([^"]*\)".*/\1/')

echo "Building backend  v${BACKEND_VERSION}"
docker build -t cms-backend:"${BACKEND_VERSION}" ./backend

echo "Building frontend v${FRONTEND_VERSION}"
docker build -t cms-frontend:"${FRONTEND_VERSION}" ./frontend

echo "Done."
echo "  cms-backend:${BACKEND_VERSION}"
echo "  cms-frontend:${FRONTEND_VERSION}"
