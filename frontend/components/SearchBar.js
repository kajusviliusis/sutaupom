"use client";

import { useState } from "react";
import { useRouter} from "next/navigation";

export default function SearchBar({ placeholder = "Ieškoti..." }) {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    
    router.push(`/pasiulymai?query=${encodeURIComponent(query)}`);
    console.log("Paieškos užklausa:", query);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full max-w-xl rounded-xl shadow-md overflow-hidden border border-gray-200 bg-white"
    >
      <div className="flex items-center px-3 text-black">
        <svg
        xmlns="http://www.w3.org/2000/svg" 
        width="24" 
        height="24" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        className="lucide lucide-search-icon lucide-search"
        >
          <path d="m21 21-4.34-4.34"/>
          <circle cx="11" cy="11" r="8"/>
          </svg>
          </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        // suppress hydration warnings caused by attribute injection (extensions) or minor SSR/client mismatches
        suppressHydrationWarning
        className="w-full px-4 py-2 text-gray-700 focus:outline-none"
      />
      <button
        type="submit"
        // suppress hydration warning for this button (some extensions inject attributes)
        suppressHydrationWarning
        className="bg-black text-white px-4 py-2 hover:bg-gray-400 transition"

      >
        Ieškoti
      </button>
    </form>
  );
}