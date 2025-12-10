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

  // Effect for query and shop (search/filter)
  useEffect(() => {
    const handleLocationChange = () => {
      const sp = new URLSearchParams(window.location.search || "");
      const q = sp.get("query")?.trim() || "";

      setTimeout(() => {
        setQuery(q);
        setLoading(true);

        if (!q) return; // Don't fetch here if no query

        // Siunčiam pasirinktus sort ir shop parametrus į API
        fetch(`/api/products?query=${encodeURIComponent(q)}&sort=${sort}&shop=${shop}`)
          .then((res) => res.json())
          .then((data) => setProducts(data))
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

  // Effect for random products (no query)
  useEffect(() => {
    const sp = new URLSearchParams(window.location.search || "");
    const q = sp.get("query")?.trim() || "";
    if (q) return;
    setLoading(true);
    // Request unbiased random sample across all shops
    fetch(`/api/products?random=true&limit=12`)
      .then((res) => res.json())
      .then((data) => {
        setProducts(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.error("Klaida gaunant produktus:", err);
        setProducts([]);
      })
      .finally(() => setLoading(false));
  }, []);

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
              onClick={() => setShop("barbora")}
              className={`btn ${shop === "barbora" ? "btn-black btn-active" : "btn-ghost"}`}
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
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
