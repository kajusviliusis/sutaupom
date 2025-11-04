"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import NavBar from '../../../components/NavBar.js';
import SearchBar from '../../../components/SearchBar.js';
import productsData from '../../../data/products.json';

export default function PasiulymaiPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get("query") || "";

  const [products, setProducts] = useState([]);

  useEffect(() => {
    if(!query.trim()) return;

    const filteredProducts = productsData.filter(p => p.name.toLowerCase().includes(query.toLowerCase())
  );

  setProducts(filteredProducts);
      
    }, [query]);

  return (
    <main className="min-h-screen bg-white">

      <NavBar />

      {/* Paieška */}
      <section className="px-4 py-8 flex justify-center">
        <SearchBar placeholder="Ieškok pasiūlymų..." />
      </section>
      <section className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-semibold mb-6">
            Pasiūlymai {query ? `: ` + query : ""}
            </h2>

            {products.length === 0 && <p>Nerasta jokių pasiūlymų.</p>}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {products.map(p => (
              <div
              key={p.id}
              className="border rounded-xl p-4 shadow hover:shadow-lg transition bg-white"
              >
                <img
                src={p.image}
                alt={p.name}
                className="w-full h-40 object-contain rounded-lg mb-3"
                />
                <h3 className="text-lg font-medium">{p.name}</h3>
                <p>Parduotuvė: {p.store}</p>
                <p>Kaina: {p.price} €</p>
                </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}