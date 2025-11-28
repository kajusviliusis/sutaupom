#!/usr/bin/env python3
import os
import sqlite3
import io
import csv
import re

ROOT = os.path.dirname(os.path.dirname(__file__))  # backend/
SCRAP_DIR = os.path.join(ROOT, 'scrapping')
SQL_PATH = os.path.join(SCRAP_DIR, 'database_sqlite.sql')
DB_DIR = os.path.join(ROOT, 'dev-data')
DB_PATH = os.path.join(DB_DIR, 'test-database.sqlite')

os.makedirs(DB_DIR, exist_ok=True)

if not os.path.exists(SQL_PATH):
    print(f"ERROR: SQL schema not found at {SQL_PATH}")
    raise SystemExit(1)

# create / reset test db
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
with open(SQL_PATH, 'r', encoding='utf-8') as f:
    sql = f.read()
conn.executescript(sql)
conn.commit()
print(f"Initialized test DB at {DB_PATH}")

csv_files = [f for f in os.listdir(SCRAP_DIR) if f.lower().endswith('.csv')]
if not csv_files:
    print("No CSV files found to import.")
    raise SystemExit(0)

stats = {"files": [], "stores_created": 0, "products_created": 0, "prices_inserted": 0}

for fname in csv_files:
    fpath = os.path.join(SCRAP_DIR, fname)
    file_stats = {"file": fname, "rows": 0, "inserted": 0, "skipped": 0}
    with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        file_stats['rows'] += 1
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
            cleaned = re.sub(r"[^0-9,\.\-]", "", str(price_raw))
            cleaned = cleaned.replace(',', '.')
            price = float(cleaned.strip())
        except Exception:
            file_stats['skipped'] += 1
            continue

        # insert store
        cur.execute("INSERT OR IGNORE INTO stores (name) VALUES (?)", (shop,))
        cur.execute("SELECT store_id FROM stores WHERE name = ?", (shop,))
        store_id = cur.fetchone()[0]

        # product
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

    stats['files'].append(file_stats)
    conn.commit()

# compute created counts
cur.execute("SELECT COUNT(*) FROM stores")
stats['stores_created'] = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products")
stats['products_created'] = cur.fetchone()[0]

conn.close()

# print results
print("\nImport results:")
for f in stats['files']:
    print(f"- {f['file']}: rows={f['rows']}, inserted={f['inserted']}, skipped={f['skipped']}")
print(f"stores_created={stats['stores_created']}, products_created={stats['products_created']}, prices_inserted={stats['prices_inserted']}")
print(f"Test DB path: {DB_PATH}")
