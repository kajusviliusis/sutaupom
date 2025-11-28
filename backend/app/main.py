from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
import os
import csv
import io

app = FastAPI(title="Products API")

# Config
DB_PATH = os.environ.get("DATABASE_PATH", "/data/database.sqlite")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")

origins = [
    "http://localhost:3000",
]
VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL:
    origins.append(VERCEL_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def get_conn():
    if not os.path.exists(DB_PATH):
        raise RuntimeError(f"Database file not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_api_key(x_api_key: Optional[str] = Header(None)):
    if ADMIN_API_KEY:
        if x_api_key != ADMIN_API_KEY:
            raise HTTPException(status_code=403, detail="Forbidden")
    return True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def list_products(limit: int = 200):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"products": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-scrape")
async def upload_scrape(file: UploadFile = File(...), _auth: bool = Depends(check_api_key)):
    content_type = file.content_type or ""
    content = await file.read()
    # CSV handler
    if "csv" in content_type or file.filename.endswith(".csv"):
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        conn = get_conn()
        cur = conn.cursor()
        inserted = 0
        for row in reader:
            # Attempt to insert common columns; adapt as needed for your schema
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO products (id, name, price) VALUES (?, ?, ?)",
                    (row.get("id"), row.get("name"), row.get("price")),
                )
                inserted += 1
            except Exception:
                # best-effort: skip rows that don't match schema
                continue
        conn.commit()
        conn.close()
        return {"status": "ok", "inserted": inserted}

    # JSON handler
    if "json" in content_type or file.filename.endswith(".json"):
        import json

        data = json.loads(content)
        if isinstance(data, dict) and "products" in data:
            items = data["products"]
        elif isinstance(data, list):
            items = data
        else:
            raise HTTPException(status_code=400, detail="JSON must be an array or {products: [...]}" )

        conn = get_conn()
        cur = conn.cursor()
        inserted = 0
        for row in items:
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO products (id, name, price) VALUES (?, ?, ?)",
                    (row.get("id"), row.get("name"), row.get("price")),
                )
                inserted += 1
            except Exception:
                continue
        conn.commit()
        conn.close()
        return {"status": "ok", "inserted": inserted}

    raise HTTPException(status_code=400, detail="Unsupported file type")
