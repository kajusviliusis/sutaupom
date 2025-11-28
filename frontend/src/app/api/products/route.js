import { readFile } from "fs/promises";
import { join } from "path";

export async function GET(request) {
  const url = new URL(request.url);
  const search = url.searchParams.toString();

  // Prefer a backend API URL provided via env; fall back to the Railway URL you provided
  const BACKEND = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'https://sutaupom-production.up.railway.app';

  try {
    // Proxy the request to the backend products endpoint
    const backendUrl = `${BACKEND.replace(/\/$/, '')}/products${search ? `?${search}` : ''}`;
    const res = await fetch(backendUrl, { method: 'GET' });
    if (!res.ok) throw new Error(`Upstream returned ${res.status}`);
    const json = await res.json();

    // If backend returns an object with { products: [...] } normalize to an array response
    const products = Array.isArray(json) ? json : json.products ?? [];

    return new Response(JSON.stringify(products), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    // On any error, fall back to the local bundled JSON (useful for offline/dev or builds)
    console.warn('Backend unavailable, falling back to bundled JSON:', err?.message || err);
    try {
      const filePath = join(process.cwd(), "data/products.json");
      const fileContents = await readFile(filePath, "utf-8");
      let products = JSON.parse(fileContents);
      // allow search filtering via query param 'query'
      const q = new URL(request.url).searchParams.get('query');
      if (q) {
        const lc = q.trim().toLowerCase();
        products = products.filter(p => p.name && p.name.toLowerCase().includes(lc));
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
