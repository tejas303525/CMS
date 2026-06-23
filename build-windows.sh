#!/usr/bin/env bash
# Build a Windows 64-bit exe using Wine + Windows Python + PyInstaller.
# Run on Linux: ./build-windows.sh
#
# Prerequisites:
#   apt install wine wine64
#   node/yarn on PATH
#
# First run downloads Python 3.11 for Windows into ~/.wine-cms-build.
# Subsequent runs skip that step and go straight to PyInstaller.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="$ROOT/target/windows"
WINE_PREFIX="$HOME/.wine-cms-build"
WIN_PYTHON="$WINE_PREFIX/drive_c/Python311/python.exe"
PYTHON_VERSION="3.11.9"
PYTHON_INSTALLER="/tmp/python-${PYTHON_VERSION}-amd64.exe"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe"

export WINEPREFIX="$WINE_PREFIX"
export WINEARCH=win64
export WINEDEBUG=fixme-all

step() { echo; echo "==> $*"; }
die()  { echo "ERR: $*" >&2; exit 1; }

# ── 1. Prerequisites ───────────────────────────────────────────────────────────
step "Checking prerequisites"
command -v wine >/dev/null || die "wine not found. Install: apt install wine wine64"
command -v yarn >/dev/null || die "yarn not found."
echo "    OK"

# ── 2. Build React frontend ────────────────────────────────────────────────────
step "Building React frontend"
(cd "$ROOT/frontend" && yarn install --frozen-lockfile --silent && yarn build --silent)
echo "    OK  →  $ROOT/build/"

# ── 3. Wine prefix + Windows Python (one-time) ────────────────────────────────
if [ ! -f "$WIN_PYTHON" ]; then
    step "One-time Wine setup (takes a few minutes)"

    if [ ! -d "$WINE_PREFIX/drive_c" ]; then
        echo "    Initialising Wine prefix..."
        wine wineboot --init 2>/dev/null
        sleep 3
    fi

    if [ ! -f "$PYTHON_INSTALLER" ]; then
        echo "    Downloading Python $PYTHON_VERSION for Windows..."
        curl -L -# -o "$PYTHON_INSTALLER" "$PYTHON_URL"
    fi

    echo "    Installing Python in Wine..."
    wine "$PYTHON_INSTALLER" /quiet InstallAllUsers=0 "TargetDir=C:\\Python311" PrependPath=0 Include_test=0 2>/dev/null

    # Wait for installer to finish
    for i in $(seq 1 30); do
        [ -f "$WIN_PYTHON" ] && break
        sleep 2
    done
    [ -f "$WIN_PYTHON" ] || die "Python installation failed. Try manually: wine $PYTHON_INSTALLER"
    echo "    OK  Python $PYTHON_VERSION installed in Wine"
fi

# ── 4. Install/sync pip packages ──────────────────────────────────────────────
step "Syncing pip packages in Wine Python"
wine "$WIN_PYTHON" -m pip install --upgrade pip --quiet 2>/dev/null
wine "$WIN_PYTHON" -m pip install --quiet \
    pyinstaller \
    fastapi \
    "uvicorn[standard]" \
    aiosqlite \
    "passlib[bcrypt]" \
    bcrypt \
    PyJWT \
    python-dotenv \
    python-multipart \
    pydantic \
    starlette \
    openpyxl \
    reportlab \
    2>/dev/null
echo "    OK"

# ── 5. Build Windows exe ───────────────────────────────────────────────────────
step "Running PyInstaller"
mkdir -p "$TARGET"

WIN_TARGET="Z:${TARGET}"
WIN_WORK="Z:/tmp/cms-pyinstaller-work"
WIN_SPEC="Z:/tmp/cms-pyinstaller-spec"
WIN_PYINSTALLER="$WINE_PREFIX/drive_c/Python311/Scripts/pyinstaller.exe"

(cd "$ROOT/backend" && wine "$WIN_PYINSTALLER" \
    launcher.py \
    --onefile \
    --name cms \
    --distpath "$WIN_TARGET" \
    --workpath "$WIN_WORK" \
    --specpath "$WIN_SPEC" \
    --paths "." \
    --collect-all uvicorn \
    --collect-all fastapi \
    --collect-all starlette \
    --collect-all aiosqlite \
    --collect-all passlib \
    --collect-all reportlab \
    --collect-all openpyxl \
    --hidden-import multipart \
    --hidden-import email_validator \
    --hidden-import bcrypt \
    --hidden-import jwt \
    --noconfirm \
    --clean \
    2>/dev/null)

[ -f "$TARGET/cms.exe" ] || die "cms.exe not found — PyInstaller failed. Re-run without 2>/dev/null to see output."
echo "    OK  cms.exe built"

# ── 6. Stage frontend build alongside exe ─────────────────────────────────────
step "Staging frontend build"
rm -rf "$TARGET/build"
cp -r "$ROOT/build" "$TARGET/build"
echo "    OK  build/ staged"

# ── Done ───────────────────────────────────────────────────────────────────────
echo
echo "  Distribution: $TARGET"
echo "  ├── cms.exe"
echo "  └── build/"
echo
echo "  Ship the entire target/windows/ folder."
echo "  On first launch, cms.exe creates cms.db and .jwt_secret next to itself."
echo "  Open http://localhost:8000 in a browser."
echo
