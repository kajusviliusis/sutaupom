"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import NavBar from "../../../components/NavBar.js";
import SearchBar from "../../../components/SearchBar.js";
import ProductCard from "../../../components/ProductCard.js";

export default function PasiulymaiPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get("query")?.trim() || ""; 

  const [products, setProducts] = useState([]); 
  const [loading, setLoading] = useState(false); 

  useEffect(() => {
    if (!query) {
      setProducts([]); 
      return;
    }

    setLoading(true);

    fetch(`/api/products?query=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((data) => setProducts(data))
      .catch((err) => {
        console.error("Klaida gaunant produktus:", err);
        setProducts([]);
      })
      .finally(() => setLoading(false));

  }, [query]);

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

          <div className="flex flex-wraip justify-left gap-6">
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
