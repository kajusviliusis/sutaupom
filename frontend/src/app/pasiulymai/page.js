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
    const handleLocationChange = () => {
      const sp = new URLSearchParams(window.location.search || "");
      const q = sp.get("query")?.trim() || "";

      setTimeout(() => {
        setQuery(q);

        if (!q) {
          setProducts([]);
          return;
        }

        setLoading(true);

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
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="font-semibold mr-2">Rūšiuoti:</span>
            <button
              onClick={() => setSort("price_asc")}
              className={`px-3 py-1 rounded border ${sort === "price_asc" ? "bg-blue-600 text-white" : "bg-white text-black border-gray-300"}`}
            >
              Kaina ↑
            </button>
            <button
              onClick={() => setSort("price_desc")}
              className={`px-3 py-1 rounded border ${sort === "price_desc" ? "bg-blue-600 text-white" : "bg-white text-black border-gray-300"}`}
            >
              Kaina ↓
            </button>
            <span className="font-semibold ml-4 mr-2">Parduotuvė:</span>
            <button
              onClick={() => setShop("")}
              className={`px-3 py-1 rounded border ${shop === "" ? "bg-green-600 text-white" : "bg-white text-black border-gray-300"}`}
            >
              Visos
            </button>
            <button
              onClick={() => setShop("rimi")}
              className={`px-3 py-1 rounded border ${shop === "rimi" ? "bg-green-600 text-white" : "bg-white text-black border-gray-300"}`}
            >
              Rimi
            </button>
            <button
              onClick={() => setShop("barbora")}
              className={`px-3 py-1 rounded border ${shop === "barbora" ? "bg-green-600 text-white" : "bg-white text-black border-gray-300"}`}
            >
              Maxima
            </button>
            <button
              onClick={() => setShop("iki")}
              className={`px-3 py-1 rounded border ${shop === "iki" ? "bg-green-600 text-white" : "bg-white text-black border-gray-300"}`}
            >
              Iki
            </button>
            <button
              onClick={() => setShop("lidl")}
              className={`px-3 py-1 rounded border ${shop === "lidl" ? "bg-green-600 text-white" : "bg-white text-black border-gray-300"}`}
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
