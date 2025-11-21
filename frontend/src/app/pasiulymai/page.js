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

        fetch(`/api/products?query=${encodeURIComponent(q)}`)
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
    // listen for back/forward navigation
    window.addEventListener("popstate", handleLocationChange);
    // make history.pushState/replaceState emit a custom event so we detect programmatic navigations
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
  }, []);

  return (
    <main className="min-h-screen bg-white">
      <NavBar />

      {/* Paieškos juosta */}
      <section className="px-4 py-8 flex justify-center">
        <SearchBar placeholder="Ieškok pasiūlymų..." />
      </section>

      {/* Rezultatų sąrašas */}
      <section className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
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
