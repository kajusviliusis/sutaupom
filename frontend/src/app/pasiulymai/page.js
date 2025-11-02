"use client";

import { useEffect, useState } from "react";
import NavBar from "../../../components/NavBar";
import SearchBar from "../../../components/SearchBar";
import ProductCard from "../../../components/ProductCard";

export default function PasiulymaiPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // fetch is mock api, veliau pakeisti tikru
  useEffect(() => {
    async function fetchProducts() {
      const res = await fetch("/api/products");
      const data = await res.json();
      setProducts(data);
      setLoading(false);
    }

    fetchProducts();
  }, []);

  return (
    <main className="min-h-screen bg-white">
      <NavBar />

      {/* paieska */}
      <section className="px-4 py-8 flex justify-center">
        <SearchBar placeholder="Ieškok pasiūlymų..." />
      </section>

      {/* pasiulymu skiltis */}
      <section className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-6">Pasiūlymai</h2>

          {loading ? (
            <p className="text-center text-gray-500">Kraunama...</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
