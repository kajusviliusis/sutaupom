#!/bin/sh
set -e
DB=/data/database.sqlite
if [ ! -f "$DB" ]; then
  echo "Initializing DB at $DB"
  if [ -f /app/scrapping/database_sqlite.sql ]; then
    # Use Python to execute the SQL dump so we don't require the sqlite3 binary in the image
    python - <<PYTHON || true
import sqlite3
conn = sqlite3.connect('$DB')
with open('/app/scrapping/database_sqlite.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
conn.executescript(sql)
conn.close()
print('DB initialized via Python')
PYTHON
  else
    echo "No database dump found at /app/scrapping/database_sqlite.sql; starting with empty DB"
  fi
fi
exec "$@"
