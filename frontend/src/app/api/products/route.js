import { readFile } from "fs/promises";
import { join } from "path";

export async function GET(request) {
  const url = new URL(request.url);
  const q = url.searchParams.get('query');
  const sort = url.searchParams.get('sort');
  const shop = url.searchParams.get('shop');
  const limitParam = url.searchParams.get('limit');

  // Prefer a backend API URL provided via env; fall back to the Railway URL
  const BACKEND = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'https://sutaupom-production.up.railway.app';

  try {
    // Only forward `limit` to the backend (backend currently supports `limit`)
    const backendUrl = `${BACKEND.replace(/\/$/, '')}/products${limitParam ? `?limit=${encodeURIComponent(limitParam)}` : ''}`;
    const res = await fetch(backendUrl, { method: 'GET' });
    if (!res.ok) throw new Error(`Upstream returned ${res.status}`);
    const json = await res.json();

    // Normalize products array
    let products = Array.isArray(json) ? json : json.products ?? [];

    // Local filtering: search and shop
    if (q) {
      const lc = q.trim().toLowerCase();
      products = products.filter(p => p.name && p.name.toLowerCase().includes(lc));
    }
    if (shop) {
      const ls = shop.trim().toLowerCase();
      products = products.filter(p => ((p.shop || p.store || '') + '').toLowerCase() === ls);
    }

    // Local sorting: support price_asc/price_desc, otherwise id desc
    const getPrice = (item) => Number(item.shelf_price ?? item.price ?? item.per_unit_price ?? 0) || 0;
    if (sort === 'price_asc') {
      products.sort((a, b) => getPrice(a) - getPrice(b));
    } else if (sort === 'price_desc') {
      products.sort((a, b) => getPrice(b) - getPrice(a));
    } else {
      products.sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
    }

    // Apply local limit if provided
    if (limitParam) {
      const n = parseInt(limitParam) || 0;
      if (n > 0) products = products.slice(0, n);
    }

    return new Response(JSON.stringify(products), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    // Fallback to bundled JSON if backend fetch fails
    console.warn('Backend unavailable, falling back to bundled JSON:', err?.message || err);
    try {
      const filePath = join(process.cwd(), "data/products.json");
      const fileContents = await readFile(filePath, "utf-8");
      let products = JSON.parse(fileContents);
      if (q) {
        const lc = q.trim().toLowerCase();
        products = products.filter(p => p.name && p.name.toLowerCase().includes(lc));
      }
      if (shop) {
        const ls = shop.trim().toLowerCase();
        products = products.filter(p => ((p.store || '') + '').toLowerCase() === ls);
      }
      if (sort === 'price_asc') {
        products.sort((a, b) => (a.price || 0) - (b.price || 0));
      } else if (sort === 'price_desc') {
        products.sort((a, b) => (b.price || 0) - (a.price || 0));
      }
      if (limitParam) {
        const n = parseInt(limitParam) || 0;
        if (n > 0) products = products.slice(0, n);
      }
      return new Response(JSON.stringify(products), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    } catch (err2) {
      console.error('Products API error (fallback failed):', err2);
      return new Response(JSON.stringify({ error: 'Server error while fetching products.' }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  }
}
