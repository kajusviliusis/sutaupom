#!/usr/bin/env python3
import csv
import sqlite3
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
SCRAPPING = ROOT / 'scrapping'
DB_DIR = ROOT / 'db'
DB_FILE = DB_DIR / 'products.db'

CSV_FILES = [
    (SCRAPPING / 'rimi_products.csv', 'rimi'),
    (SCRAPPING / 'barbora_all_pages.csv', 'barbora'),
    (SCRAPPING / 'iki_products.csv', 'iki'),
]


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


def parse_price(price_str):
    """Extract numeric value from price string (e.g., '1.39 €' -> 1.39)"""
    if not price_str:
        return None
    match = re.search(r'[\d.,]+', str(price_str))
    if match:
        try:
            return float(match.group().replace(',', '.'))
        except ValueError:
            return None
    return None


def seed_from_csv(conn, csv_path, shop_name):
    """Import CSV file based on shop type"""
    if not csv_path.exists():
        print(f"⚠ CSV not found: {csv_path}")
        return 0

    inserted = 0
    try:
        with csv_path.open(newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            rows = []
            
            for r in reader:
                if shop_name == 'iki':
                    name = r.get('product_name', '')
                    shelf = parse_price(r.get('shelf_price'))
                    unit = parse_price(r.get('per_unit_price'))
                    image = r.get('image_url', '')
                else:  # rimi, barbora
                    name = r.get('name', '')
                    shelf = parse_price(r.get('price'))
                    unit = parse_price(r.get('discount_price'))
                    image = r.get('image_url', '')
                
                if name and name.strip():
                    rows.append((name, shelf, unit, image, shop_name))
            
            if rows:
                cur = conn.cursor()
                cur.executemany(
                    'INSERT INTO products (name, shelf_price, per_unit_price, image_url, shop) VALUES (?, ?, ?, ?, ?)',
                    rows,
                )
                inserted = cur.rowcount
                conn.commit()
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
    
    return inserted


def main():
    ensure_db_dir()
    conn = sqlite3.connect(DB_FILE)
    create_table(conn)

    # Clear existing rows to allow re-seed
    conn.execute('DELETE FROM products')
    conn.commit()

    total_count = 0
    for csv_path, shop_name in CSV_FILES:
        count = seed_from_csv(conn, csv_path, shop_name)
        total_count += count
        print(f"✓ {shop_name.upper()}: Inserted {count} rows")

    conn.close()
    print(f"\n✓ Total: {total_count} products imported into {DB_FILE}")


if __name__ == '__main__':
    main()
