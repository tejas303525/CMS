# CMS — Church Management System

A Dockerized app: MongoDB + FastAPI backend (`backend/`) + React frontend (`frontend/`), run via `docker compose`. See `DOCKER_GUIDE.md` and `SETUP_GUIDE.md` for operational details.

## Before touching a live/production instance

This runs on real production data (hundreds of member records with PII: names, contact info, DOB). Before pulling new code, rebuilding images, restarting containers, or running any command that touches the `mongo` volume (`docker compose down -v`, `restore.ps1`/`restore.sh`, etc.) on a machine that has real data:

1. Run the backup script first — no exceptions:
   ```powershell
   .\backup.ps1
   ```
   (`./backup.sh` on Linux/macOS). Confirm it actually wrote a non-empty `church-backup.gz` under `backups\<timestamp>\` before proceeding.
2. Only then pull/build/restart (`git pull`, `.\build.ps1`, `docker compose down && docker compose up -d`).
3. After restarting, verify the app is actually healthy (containers `docker compose ps` all "running", log in, check the members list loads) before considering the deploy done.
4. If anything looks wrong, restore the backup from step 1 with `restore.ps1`/`restore.sh` rather than trying to patch forward on bad data.

Do not skip the backup because "it's just a small change" — the backup takes seconds and the data does not come back if something goes wrong.
