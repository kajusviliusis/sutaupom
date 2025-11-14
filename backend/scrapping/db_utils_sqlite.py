import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("data.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def save_product_record(*, name, price, discount_price, image_url, store_name):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO stores(name) VALUES(?)", (store_name,))
        cur.execute("SELECT store_id FROM stores WHERE name=?", (store_name,))
        store_id = cur.fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO products(name, image_url) VALUES(?, ?)", (name, image_url))
        cur.execute("SELECT product_id FROM products WHERE name=?", (name,))
        product_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO prices (product_id, store_id, price, discount_price, timestamp) VALUES (?, ?, ?, ?, ?)",
            (product_id, store_id, price, discount_price, datetime.now())
        )
        conn.commit()