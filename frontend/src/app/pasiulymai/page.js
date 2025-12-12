"use client";
import { useEffect, useState } from "react";
import NavBar from "../../../components/NavBar.js";
import SearchBar from "../../../components/SearchBar.js";
import ProductCard from "../../../components/ProductCard.js";

export const dynamic = 'force-dynamic';


export default function PasiulymaiPage() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sort, setSort] = useState(""); // default: nerūšiuota pagal kainą
  const [shop, setShop] = useState(""); // default: visos parduotuvės

  useEffect(() => {
    if (typeof window === "undefined") return; // Tik naršyklėje
    const handleLocationChange = () => {
      const sp = new URLSearchParams(window.location.search || "");
      const q = sp.get("query")?.trim() || "";

      setTimeout(() => {
        setQuery(q);
        setLoading(true);

        // Jei yra paieška, visada filtruojam pagal query, sort, shop
        if (q) {
          fetch(`/api/products?query=${encodeURIComponent(q)}&sort=${sort}&shop=${shop}`)
            .then((res) => res.json())
            .then((data) => setProducts(dedupeByProductMinPrice(data)))
            .catch((err) => {
              console.error("Klaida gaunant produktus:", err);
              setProducts([]);
            })
            .finally(() => setLoading(false));
          return;
        }

        // Jei nėra paieškos, bet yra pasirinktas sort arba shop, filtruojam pagal juos
        if (sort || shop) {
          fetch(`/api/products?sort=${sort}&shop=${shop}`)
            .then((res) => res.json())
            .then((data) => setProducts(dedupeByProductMinPrice(data)))
            .catch((err) => {
              console.error("Klaida gaunant produktus:", err);
              setProducts([]);
            })
            .finally(() => setLoading(false));
          return;
        }

        // Jei nėra nieko pasirinkta, rodom random 100 produktu
          fetch(`/api/products?random=true&limit=100`)
          .then((res) => res.json())
          .then((data) => {
            const arr = Array.isArray(data) ? data : [];
            setProducts(dedupeByProductMinPrice(arr));
          })
          .catch((err) => {
            console.error("Klaida gaunant produktus:", err);
            setProducts([]);
          })
          .finally(() => setLoading(false));
      }, 0);
    };

    handleLocationChange();
    window.addEventListener("popstate", handleLocationChange);
    const origPush = history.pushState;
    const origReplace = history.replaceState;

    history.pushState = function () {
      const result = origPush.apply(this, arguments);
      window.dispatchEvent(new Event("locationchange"));
      return result;
    };

    history.replaceState = function () {
      const result = origReplace.apply(this, arguments);
      window.dispatchEvent(new Event("locationchange"));
      return result;
    };

    window.addEventListener("locationchange", handleLocationChange);

    return () => {
      window.removeEventListener("popstate", handleLocationChange);
      window.removeEventListener("locationchange", handleLocationChange);
      history.pushState = origPush;
      history.replaceState = origReplace;
    };
  }, [sort, shop]);

  return (
    <main className="min-h-screen bg-white">
      <NavBar />

      {/* Pranešimas apie nuolaidas */}
      <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 max-w-3xl mx-auto mt-6 mb-2 rounded">
        <p className="font-medium">Kai kurios nuolaidos parduotuvėse taikomos tik su lojalumo kortele arba perkant dvi ar daugiau prekių.</p>
      </div>

      {/* Paieškos juosta */}
      <section className="px-4 py-8 flex justify-center">
        <SearchBar placeholder="Ieškok pasiūlymų..." />
      </section>

      {/* Filtrų ir rūšiavimo mygtukai */}
      <section className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-wrap gap-2 mb-4 items-center">
            <span className="btn-label mr-2">Rūšiuoti:</span>
            <button
              onClick={() => setSort("price_asc")}
              className={`btn ${sort === "price_asc" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Kaina ↑
            </button>
            <button
              onClick={() => setSort("price_desc")}
              className={`btn ${sort === "price_desc" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Kaina ↓
            </button>
            <span className="btn-label ml-4 mr-2">Parduotuvė:</span>
            <button
              onClick={() => setShop("")}
              className={`btn ${shop === "" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Visos
            </button>
            <button
              onClick={() => setShop("rimi")}
              className={`btn ${shop === "rimi" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Rimi
            </button>
            <button
              onClick={() => setShop("maxima")}
              className={`btn ${shop === "maxima" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Maxima
            </button>
            <button
              onClick={() => setShop("iki")}
              className={`btn ${shop === "iki" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Iki
            </button>
            <button
              onClick={() => setShop("lidl")}
              className={`btn ${shop === "lidl" ? "btn-black btn-active" : "btn-ghost"}`}
            >
              Lidl
            </button>
          </div>
          <h2 className="text-2xl font-semibold mb-6">
            Pasiūlymai {query ? `: ${query}` : ""}
          </h2>

          {loading && <p>Įkeliama...</p>}
          {!loading && products.length === 0 && <p>Nerasta jokių pasiūlymų.</p>}

          <div className="flex flex-wrap justify-left gap-6">
            {products
              .filter((p) => p && p.shelf_price != null)
              .map((p, idx) => (
                <ProductCard key={`${p.id}-${p.shop ?? ''}-${p.shelf_price}-${idx}`} product={p} />
              ))}
          </div>
        </div>
      </section>
    </main>
  );
}

// Pašaliname pasikartojimus: paliekame po vieną įrašą kiekvienam produktui,
// parenkant mažiausią kainą (ir jos parduotuvę).
function dedupeByProductMinPrice(items) {
  try {
    const byId = new Map();
    for (const r of items || []) {
      if (!r) continue;
      const id = r.id ?? r.product_id ?? r.name; // fallback jeigu nėra id
      const price = Number(r.shelf_price);
      if (!id || Number.isNaN(price)) continue;
      const cur = byId.get(id);
      if (!cur || price < Number(cur.shelf_price)) {
        byId.set(id, r);
      }
    }
    let result = Array.from(byId.values());
    // pritaikome esamą rūšiavimą, jei pasirinktas
    return result;
  } catch {
    return Array.isArray(items) ? items : [];
  }
}
