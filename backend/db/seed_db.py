#!/usr/bin/env python3
import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRAPING = ROOT / 'scrapping'
CSV_FILE = SCRAPING / 'rimi_products.csv'
DB_DIR = ROOT / 'db'
DB_FILE = DB_DIR / 'products.db'


def ensure_db_dir():
    DB_DIR.mkdir(parents=True, exist_ok=True)


def create_table(conn):
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            shelf_price REAL,
            per_unit_price REAL,
            image_url TEXT,
            shop TEXT
        )
        '''
    )


def seed_from_csv(conn, csv_path, shop_name=None):
    inserted = 0
    with csv_path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = []
        for idx, r in enumerate(reader):
            # Ensure name is always filled
            name = r.get('product_name') or r.get('name') or r.get('title') or ''
            if not name:
                # fallback: try shop_name + idx if empty
                name = f"{r.get('shop_name', shop_name)}_{idx}" if (r.get('shop_name') or shop_name) else f"produktas_{idx}"
            price_text = r.get('price') or r.get('shelf_price') or r.get('kaina') or ''
            if not price_text and r.get('title'):
                price_text = r.get('price') or ''
            try:
                if isinstance(price_text, (int, float)):
                    shelf = float(price_text)
                else:
                    shelf_str = str(price_text).replace('€', '').replace('â‚¬', '').replace(',', '.').strip()
                    shelf = float(shelf_str) if shelf_str else None
            except Exception:
                shelf = None
            try:
                unit = float(r.get('per_unit_price') or 0)
            except Exception:
                unit = None
            image = r.get('image_url') or r.get('image') or r.get('image_small') or ''
            shop = (r.get('shop_name') or shop_name or r.get('shop') or 'rimi')
            if shop:
                shop = str(shop).strip().lower()
            rows.append((name, shelf, unit, image, shop))

        cur = conn.cursor()
        cur.executemany(
            'INSERT INTO products (name, shelf_price, per_unit_price, image_url, shop) VALUES (?, ?, ?, ?, ?)',
            rows,
        )
        inserted = cur.rowcount
        conn.commit()
    return inserted


def main():
    ensure_db_dir()
    conn = sqlite3.connect(DB_FILE)
    create_table(conn)

    # Clear existing rows to allow re-seed; comment out if unwanted
    conn.execute('DELETE FROM products')
    conn.commit()

    count = 0
    # Import Rimi
    rimi_csv = SCRAPING / 'rimi_products.csv'
    if rimi_csv.exists():
        count += seed_from_csv(conn, rimi_csv, shop_name='Rimi')
    else:
        print(f"CSV file not found: {rimi_csv}")

    # Import Barbora
    barbora_csv = SCRAPING / 'barbora_all_pages.csv'
    if barbora_csv.exists():
        count += seed_from_csv(conn, barbora_csv, shop_name='barbora')
    else:
        print(f"CSV file not found: {barbora_csv}")

    # Import Iki
    iki_csv = SCRAPING / 'iki_products.csv'
    if iki_csv.exists():
        count += seed_from_csv(conn, iki_csv, shop_name='iki')
    else:
        print(f"CSV file not found: {iki_csv}")

    # Import Lidl
    lidl_csv = SCRAPING / 'lidl_products.csv'
    if lidl_csv.exists():
        count += seed_from_csv(conn, lidl_csv, shop_name='lidl')
    else:
        print(f"CSV file not found: {lidl_csv}")
    print(f"Inserted {count} rows into {DB_FILE}")
    conn.close()


if __name__ == '__main__':
    main()
