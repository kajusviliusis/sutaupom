"use client";

import Link from "next/link";

export default function NavBar() {
  return (
    <div className="p-4 border-b border-gray-100">
      <div className="flex justify-center items-center max-w-7xl mx-auto text-sm md:text-base font-medium">
        <Link href="/" className="mx-4 text-gray-600 hover:text-gray-900">Pagrindinis</Link>
        <Link href="/pasiulymai" className="mx-4 text-gray-600 hover:text-gray-900">Pasiūlymai</Link>
        <Link href="/apie-mus" className="mx-4 text-gray-600 hover:text-gray-900">Apie mus</Link>
      </div>
    </div>
  );
}
// NavBar component removed — navigation is handled inline in `src/app/page.js`.
// This file is kept as a placeholder and intentionally exports nothing to
// avoid accidental usage. Remove the file if you want it fully deleted.

// Placeholder (no exports)
