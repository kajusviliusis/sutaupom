PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stores (
    store_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE,
    url        TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    image_url  TEXT,
    UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS prices (
    price_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id     INTEGER NOT NULL,
    store_id       INTEGER NOT NULL,
    price          REAL NOT NULL,
    discount_price REAL,
    timestamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (store_id)   REFERENCES stores(store_id)
);