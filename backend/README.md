# Backend (FastAPI) — run & deploy

This backend is a minimal FastAPI service that reads a SQLite database from the path provided in the `DATABASE_PATH` environment variable (default: `/data/database.sqlite`). It is designed for local development and deployment to hosts that provide a writable volume (Railway, Oracle VM, etc.).

Files added:

- `backend/app/main.py` — FastAPI app with `/products` and `/upload-scrape` endpoints.
- `backend/requirements.txt` — Python dependencies.
- `backend/Dockerfile` — Docker image used for container deploys.
- `backend/entrypoint.sh` — initializes the DB on first run using `/app/scrapping/database_sqlite.sql` if present.

Local development (no Docker)

1. Create a Python venv and install requirements:
```
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```
2. Set `DATABASE_PATH` to point to your sqlite file, e.g. `C:\full\path\to\backend\scrapping\database.sqlite`.
```
set DATABASE_PATH=C:\full\path\to\backend\scrapping\database.sqlite
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Local development with Docker Compose

1. Ensure Docker is installed.
2. Start the service (this will mount `./dev-data` as `/data` inside the container):
```
docker compose up --build
```
3. The API will be available at `http://localhost:8000`.

Deploying to Railway (mount volume)

1. Push repo to GitHub.
2. Create a new Railway service (container) and connect your repo.
3. Add a volume (Railway free 0.5 GB) and mount it to `/data`.
4. Set environment variables in Railway:
   - `DATABASE_PATH=/data/database.sqlite`
   - `ADMIN_API_KEY=...` (optional)
5. Deploy and test the service URL.

Notes

- The upload endpoint uses `INSERT OR IGNORE` into `products (id, name, price)`. Modify to match your actual schema.
- SQLite is fine for a small class project, but keep the DB size below your provider's volume limit and schedule backups.

