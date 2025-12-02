from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
import os
import csv
import io
from fastapi.responses import Response

app = FastAPI(title="Products API")

DB_PATH = os.environ.get("DATABASE_PATH", "/data/database.sqlite")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")

origins = ["http://localhost:3000"]
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
    if "csv" in content_type or file.filename.endswith(".csv"):
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        conn = get_conn()
        cur = conn.cursor()
        inserted = 0
        for row in reader:
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


@app.post("/admin/init-db")
def init_db(_auth: bool = Depends(check_api_key)):
    if os.path.exists(DB_PATH):
        return {"status": "exists", "path": DB_PATH}

    dump_path = "/app/scrapping/database_sqlite.sql"
    if not os.path.exists(dump_path):
        raise HTTPException(status_code=500, detail=f"SQL dump not found at {dump_path}")

    try:
        conn = sqlite3.connect(DB_PATH)
        with open(dump_path, "r", encoding="utf-8") as f:
            sql = f.read()
        conn.executescript(sql)
        conn.close()
        return {"status": "initialized", "path": DB_PATH}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/status")
def admin_status(_auth: bool = Depends(check_api_key)):
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail=f"Database file not found at {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        result = {}
        for t in tables:
            try:
                cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception as e:
                cnt = f"error: {e}"
            result[t] = cnt
        conn.close()
        return {"path": DB_PATH, "tables": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/dump")
def admin_dump(_auth: bool = Depends(check_api_key)):
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail=f"Database file not found at {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        buf = io.StringIO()
        for line in conn.iterdump():
            buf.write(f"{line}\n")
        conn.close()
        sqltext = buf.getvalue()
        return Response(content=sqltext, media_type="application/sql")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/import-csvs")
def admin_import_csvs(_auth: bool = Depends(check_api_key)):
    scrapping_dir = "/app/scrapping"
    if not os.path.exists(scrapping_dir):
        raise HTTPException(status_code=500, detail=f"scrapping directory not found at {scrapping_dir}")

    csv_files = [f for f in os.listdir(scrapping_dir) if f.lower().endswith('.csv')]
    if not csv_files:
        return {"status": "no_csv_found", "files": []}

    stats = {"files": [], "stores_created": 0, "products_created": 0, "prices_inserted": 0, "errors": 0}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for fname in csv_files:
        fpath = os.path.join(scrapping_dir, fname)
        file_stats = {"file": fname, "rows": 0, "inserted": 0, "skipped": 0}
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
                text = fh.read()
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                file_stats["rows"] += 1
                shop = (
                    row.get('shop_name')
                    or row.get('shop')
                    or row.get('store')
                    or row.get('shopName')
                )
                pname = (
                    row.get('product_name')
                    or row.get('product')
                    or row.get('name')
                    or row.get('productName')
                    or row.get('title')
                )
                price_raw = (
                    row.get('shelf_price')
                    or row.get('price')
                    or row.get('shelfPrice')
                )
                image = (
                    row.get('image_url')
                    or row.get('image')
                    or row.get('imageUrl')
                    or row.get('image_small')
                )

                if not shop:
                    inferred = os.path.splitext(fname)[0]
                    inferred = inferred.split('_')[0].split('-')[0].split('.')[0]
                    shop = inferred

                if not pname or not price_raw:
                    file_stats['skipped'] += 1
                    continue

                try:
                    import re

                    cleaned = re.sub(r"[^0-9,\.\-]", "", str(price_raw))
                    cleaned = cleaned.replace(',', '.')
                    price = float(cleaned.strip())
                except Exception:
                    file_stats['skipped'] += 1
                    continue

                cur.execute("INSERT OR IGNORE INTO stores (name) VALUES (?)", (shop,))
                cur.execute("SELECT store_id FROM stores WHERE name = ?", (shop,))
                store_id = cur.fetchone()[0]

                if image:
                    cur.execute("INSERT OR IGNORE INTO products (name, image_url) VALUES (?, ?)", (pname, image))
                    cur.execute("SELECT product_id, image_url FROM products WHERE name = ?", (pname,))
                    prow = cur.fetchone()
                    product_id = prow[0]
                    existing_image = prow[1]
                    if existing_image in (None, '') and image:
                        cur.execute("UPDATE products SET image_url = ? WHERE product_id = ?", (image, product_id))
                else:
                    cur.execute("INSERT OR IGNORE INTO products (name) VALUES (?)", (pname,))
                    cur.execute("SELECT product_id FROM products WHERE name = ?", (pname,))
                    product_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO prices (product_id, store_id, price) VALUES (?, ?, ?)",
                    (product_id, store_id, price),
                )
                file_stats['inserted'] += 1
                stats['prices_inserted'] += 1

        except Exception as e:
            stats['errors'] += 1
            file_stats['error'] = str(e)

        stats['files'].append(file_stats)

    conn.commit()
    try:
        cur.execute("SELECT COUNT(*) FROM stores")
        stats['stores_created'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products")
        stats['products_created'] = cur.fetchone()[0]
    except Exception:
        pass

    conn.close()
    return stats
