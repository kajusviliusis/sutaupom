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
    const offsetParam = url.searchParams.get("offset");
    // limitai produktu kiek rodyti
    const limit = Math.max(1, Math.min(10000, Number(limitParam) || 500));
    const offset = Math.max(0, Math.min(1000000, Number(offsetParam) || 0));

    // ima duomenis is backendo railway
    const backendBase = process.env.NEXT_PUBLIC_API_URL
    if (backendBase) {
      const params = new URLSearchParams();
      params.set("limit", String(limit));
      if (search) params.set("query", search);
      if (shop) params.set("shop", shop);
      if (sort) params.set("sort", sort);
      if (random) params.set("random", "true");
      if (offset) params.set("offset", String(offset));

      try {
        const resp = await fetch(`${backendBase.replace(/\/$/, "")}/products?${params.toString()}`, {
          method: "GET",
          headers: { "Accept": "application/json" },
          next: { revalidate: 60 },
        });
        if (resp.ok) {
          const data = await resp.json();
          const products = Array.isArray(data) ? data : data.products || [];
          return new Response(JSON.stringify(products), {
            status: 200,
            headers: { "Content-Type": "application/json", "X-Data-Source": "backend" },
          });
        }
        console.warn("Backend fetch failed:", resp.status, await resp.text());
      } catch (e) {
        console.warn("Backend unreachable, using local fallback:", e?.message || e);
      }
    }

    // fallback
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
      headers: { "Content-Type": "application/json", "X-Data-Source": "local-fallback" },
    });
  } catch (err) {
    console.error("Products API error:", err);
    return new Response(JSON.stringify({ error: "Server error while fetching products." }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
