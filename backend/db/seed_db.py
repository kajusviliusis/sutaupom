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


def seed_from_csv(conn, csv_path):
    inserted = 0
    with csv_path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = []
        for r in reader:
            name = r.get('product_name') or r.get('name') or ''
            try:
                shelf = float(r.get('shelf_price') or 0)
            except Exception:
                shelf = None
            try:
                unit = float(r.get('per_unit_price') or 0)
            except Exception:
                unit = None
            image = r.get('image_url') or r.get('image') or ''
            rows.append((name, shelf, unit, image, 'rimi'))

        cur = conn.cursor()
        cur.executemany(
            'INSERT INTO products (name, shelf_price, per_unit_price, image_url, shop) VALUES (?, ?, ?, ?, ?)',
            rows,
        )
        inserted = cur.rowcount
        conn.commit()
    return inserted


def main():
    if not CSV_FILE.exists():
        print(f"CSV file not found: {CSV_FILE}")
        return

    ensure_db_dir()
    conn = sqlite3.connect(DB_FILE)
    create_table(conn)

    # Clear existing rows to allow re-seed; comment out if unwanted
    conn.execute('DELETE FROM products')
    conn.commit()

    count = seed_from_csv(conn, CSV_FILE)
    print(f"Inserted {count} rows into {DB_FILE}")
    conn.close()


if __name__ == '__main__':
    main()
