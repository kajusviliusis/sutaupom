import { readFile } from 'fs/promises';
import { join } from 'path';

function parsePrice(raw) {
  if (!raw) return 0;
  return Number(String(raw).replace(/€/g, '').replace(/\s/g, '').replace(/,/g, '.')) || 0;
}

function parseBarboraCSV(raw, query, limit = 500) {
  const lines = raw.split('\n').filter(Boolean);
  if (lines.length <= 1) return [];
  const [, ...rows] = lines;
  const out = [];
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const m = row.match(/^\s*"([^"]+)"\s*,\s*([^,]+)\s*,\s*(.+)\s*$/) || row.match(/^\s*([^,]+)\s*,\s*([^,]+)\s*,\s*(.+)\s*$/);
    if (!m) continue;
    const name = (m[1] || m[1])?.trim();
    const price = parsePrice(m[2]);
    const image = (m[3] || '').trim();
    if (query && name && !name.toLowerCase().includes(query)) continue;
    out.push({ id: `barbora-${i+1}`, name, shelf_price: price, image, shop: 'barbora' });
    if (out.length >= limit) break;
  }
  return out;
}

function parseIkiCSV(raw, query, limit = 500) {
  const lines = raw.split('\n').filter(Boolean);
  if (lines.length <= 1) return [];
  const [, ...rows] = lines;
  const out = [];
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const m = row.match(/^\s*"([^"]+)"\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*(.+)\s*$/) || row.match(/^\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*(.+)\s*$/);
    if (!m) continue;
    const name = (m[1] || m[1])?.trim();
    const shelf_price = parsePrice(m[2]);
    const per_unit_price = parsePrice(m[3]);
    const image = (m[4] || '').trim();
    if (query && name && !name.toLowerCase().includes(query)) continue;
    out.push({ id: `iki-${i+1}`, name, shelf_price, per_unit_price, image, shop: 'iki' });
    if (out.length >= limit) break;
  }
  return out;
}

function parseRimiCSV(raw, query, limit = 500) {
  const lines = raw.split('\n').filter(Boolean);
  if (lines.length <= 1) return [];
  const [, ...rows] = lines;
  const out = [];
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    // name,price,discount_price,image_url
    const m = row.match(/^\s*"([^"]+)"\s*,\s*([^,]*)\s*,\s*([^,]*)\s*,\s*(.+)\s*$/) || row.match(/^\s*([^,]+)\s*,\s*([^,]*)\s*,\s*([^,]*)\s*,\s*(.+)\s*$/);
    if (!m) continue;
    const name = (m[1] || m[1])?.trim();
    const price = parsePrice(m[2]);
    const discount_price = parsePrice(m[3]);
    const image = (m[4] || '').trim();
    if (query && name && !name.toLowerCase().includes(query)) continue;
    out.push({ id: `rimi-${i+1}`, name, shelf_price: price, discount_price, image, shop: 'rimi' });
    if (out.length >= limit) break;
  }
  return out;
}

const csvCandidates = {
  barbora: [
    join(process.cwd(), '..', 'backend', 'scrapping', 'barbora_all_pages.csv'),
    join(process.cwd(), 'backend', 'scrapping', 'barbora_all_pages.csv'),
    join(process.cwd(), 'scrapping', 'barbora_all_pages.csv'),
  ],
  rimi: [
    join(process.cwd(), '..', 'backend', 'scrapping', 'rimi_products.csv'),
    join(process.cwd(), 'backend', 'scrapping', 'rimi_products.csv'),
    join(process.cwd(), 'scrapping', 'rimi_products.csv'),
  ],
  iki: [
    join(process.cwd(), '..', 'backend', 'scrapping', 'iki_products.csv'),
    join(process.cwd(), 'backend', 'scrapping', 'iki_products.csv'),
    join(process.cwd(), 'scrapping', 'iki_products.csv'),
  ],
};

async function findExisting(pathCandidates) {
  const fs = await import('fs');
  for (const p of pathCandidates) if (fs.existsSync(p)) return p;
  return null;
}

export async function GET(request) {
  try {
    const url = new URL(request.url);
    const query = url.searchParams.get('query')?.trim()?.toLowerCase() || '';
    const shopParam = url.searchParams.get('shop')?.trim()?.toLowerCase();
    const shop = shopParam || 'all';

    // 1) Try SQLite (if available) — when shop === 'all' do not filter by shop
    try {
      const sqlite = await import('better-sqlite3').then(m => m.default || m);
      const candidates = [
        join(process.cwd(), 'backend', 'db', 'products.db'),
        join(process.cwd(), 'sutaupom', 'backend', 'db', 'products.db'),
        join(process.cwd(), '..', 'sutaupom', 'backend', 'db', 'products.db'),
        join(process.cwd(), '..', 'backend', 'db', 'products.db'),
      ];
      const fs = await import('fs');
      let dbPath = null;
      for (const c of candidates) if (fs.existsSync(c)) { dbPath = c; break; }
      if (!dbPath) throw new Error('products.db not found');

      const db = sqlite(dbPath, { readonly: true, fileMustExist: true });

      let rows;
      if (query) {
        const q = `%${query}%`;
        if (shop === 'all') {
          rows = db.prepare('SELECT id, name, shelf_price, per_unit_price, image_url, shop FROM products WHERE LOWER(name) LIKE ? LIMIT 200').all(q);
        } else {
          rows = db.prepare('SELECT id, name, shelf_price, per_unit_price, image_url, shop FROM products WHERE LOWER(name) LIKE ? AND LOWER(shop) = ? LIMIT 200').all(q, shop);
        }
      } else {
        if (shop === 'all') rows = db.prepare('SELECT id, name, shelf_price, per_unit_price, image_url, shop FROM products LIMIT 500').all();
        else rows = db.prepare('SELECT id, name, shelf_price, per_unit_price, image_url, shop FROM products WHERE LOWER(shop) = ? LIMIT 500').all(shop);
      }

      const products = rows.map(r => ({ id: r.id, name: r.name, shelf_price: r.shelf_price, per_unit_price: r.per_unit_price, image: r.image_url, shop: r.shop }));
      db.close && db.close();

      return new Response(JSON.stringify(products), { status: 200, headers: { 'Content-Type': 'application/json' } });
    } catch (sqliteErr) {
      // Not using DB — fall through to CSV/JSON fallback
      // console.warn('SQLite unavailable or DB missing', sqliteErr?.message || sqliteErr);
    }

    // 2) CSV fallback: prefer CSV files (Barbora and IKI). Default to both when shop==='all'
    const [barboraPath, ikiPath] = await Promise.all([findExisting(csvCandidates.barbora), findExisting(csvCandidates.iki)]);

    const barboraResults = (barboraPath && (shop === 'all' || shop === 'barbora')) ? parseBarboraCSV(await readFile(barboraPath, 'utf8'), query, 500) : [];
    const ikiResults = (ikiPath && (shop === 'all' || shop === 'iki')) ? parseIkiCSV(await readFile(ikiPath, 'utf8'), query, 500) : [];
    // add Rimi CSV parsing fallback
    const rimiPath = await findExisting(csvCandidates.rimi);
    const rimiResults = (rimiPath && (shop === 'all' || shop === 'rimi')) ? parseRimiCSV(await readFile(rimiPath, 'utf8'), query, 500) : [];

    if (shop === 'barbora' && barboraResults.length) return new Response(JSON.stringify(barboraResults), { status: 200, headers: { 'Content-Type': 'application/json' } });
    if (shop === 'iki' && ikiResults.length) return new Response(JSON.stringify(ikiResults), { status: 200, headers: { 'Content-Type': 'application/json' } });
    if (shop === 'all' && (barboraResults.length || ikiResults.length || rimiResults.length)) return new Response(JSON.stringify(barboraResults.concat(ikiResults).concat(rimiResults).slice(0, 1000)), { status: 200, headers: { 'Content-Type': 'application/json' } });

    // 3) Final fallback: frontend/data/products.json (used in examples)
    const filePath = join(process.cwd(), 'data', 'products.json');
    const fileContents = await readFile(filePath, 'utf-8');
    let products = JSON.parse(fileContents || '[]');

    if (shop && shop !== 'all') {
      const sf = shop;
      products = products.filter(p => ((p.shop || p.store || '').toLowerCase() === sf));
    }
    if (query) {
      products = products.filter(p => p.name && p.name.toLowerCase().includes(query));
    }

    return new Response(JSON.stringify(products.slice(0, 1000)), { status: 200, headers: { 'Content-Type': 'application/json' } });
  } catch (err) {
    console.error('Products API error:', err);
    return new Response(JSON.stringify({ error: 'Server error while fetching products.' }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }
}
