import { readFile } from "fs/promises";
import { join } from "path";

export async function GET(request) {
  try {
    const url = new URL(request.url);
    const search = url.searchParams.get("query");

    const sort = url.searchParams.get("sort");
    const shop = url.searchParams.get("shop");
    const random = url.searchParams.get("random") === "true";
    const limitParam = url.searchParams.get("limit");
    const limit = Math.max(1, Math.min(1000, Number(limitParam) || 500));


    // Try to read from SQLite DB first (better for real deployments).
    try {
      const sqlite = await import('better-sqlite3').then(m => m.default || m);

      // Try several candidate locations because Next.js may run with a different working directory
      const candidates = [
        join(process.cwd(), 'backend', 'db', 'products.db'),
        join(process.cwd(), 'sutaupom', 'backend', 'db', 'products.db'),
        join(process.cwd(), '..', 'sutaupom', 'backend', 'db', 'products.db'),
        join(process.cwd(), '..', 'backend', 'db', 'products.db'),
      ];

      let dbPath = null;
      const fs = await import('fs');
      for (const c of candidates) {
        if (fs.existsSync(c)) {
          dbPath = c;
          break;
        }
      }

      if (!dbPath) throw new Error('products.db not found in any candidate path');

      const db = sqlite(dbPath, { readonly: true, fileMustExist: true });

      let rows;
      // Nauja SQL logika su filtravimu ir rusiavimu
      let sql = "SELECT id, name as product_name, shelf_price, per_unit_price, image_url, shop FROM products WHERE 1=1";
      let params = [];

      if (search) {
        sql += " AND LOWER(name) LIKE ?";
        params.push(`%${search.trim().toLowerCase()}%`);
      }
      if (shop) {
        sql += " AND LOWER(shop) = ?";
        params.push(shop.toLowerCase());
      }
      if (random) {
        sql += " ORDER BY RANDOM()";
      } else if (sort === "price_asc") {
        sql += " ORDER BY shelf_price ASC";
      } else if (sort === "price_desc") {
        sql += " ORDER BY shelf_price DESC";
      } else {
        sql += " ORDER BY id DESC";
      }
      sql += " LIMIT " + limit;
      rows = db.prepare(sql).all(...params);

      const products = rows.map(r => ({
        id: r.id,
        name: r.product_name,
        shelf_price: r.shelf_price,
        per_unit_price: r.per_unit_price,
        image: r.image_url,
        shop: r.shop,
      }));

      db.close && db.close();

      return new Response(JSON.stringify(products), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (err) {
      // If SQLite isn't available (e.g. missing native module) fall back to JSON file
      console.warn('SQLite unavailable or DB missing, falling back to JSON:', err?.message || err);
      const filePath = join(process.cwd(), "data/products.json");
      const fileContents = await readFile(filePath, "utf-8");
      let products = JSON.parse(fileContents);
      if (search) {
        const q = search.trim().toLowerCase();
        products = products.filter((p) => p.name && p.name.toLowerCase().includes(q));
      }
      if (shop) {
        products = products.filter((p) => (p.shop || p.store || "").toLowerCase() === shop.toLowerCase());
      }
      if (random) {
        products = products
          .map((p, i) => ({ p, r: Math.random(), i }))
          .sort((a, b) => a.r - b.r || a.i - b.i)
          .slice(0, limit)
          .map(({ p }) => p);
      } else {
        products = products.slice(0, limit);
      }

      return new Response(JSON.stringify(products), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }
  } catch (err) {
    console.error("Products API error:", err);
    return new Response(JSON.stringify({ error: "Server error while fetching products." }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
