import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("data.db")
SQL_PATH = Path(__file__).with_name("database_sqlite.sql")

conn = sqlite3.connect(DB_PATH)
with open(SQL_PATH, "r", encoding="utf-8") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Duomenų bazė sukurta:", DB_PATH)