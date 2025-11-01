"use client";
import NavBar from '../../../components/NavBar.js';
import SearchBar from '../../../components/SearchBar.js';

export default function PasiulymaiPage() {
  return (
    <main className="min-h-screen bg-white">

      <NavBar />

      {/* Paieška */}
      <section className="px-4 py-8 flex justify-center">
        <SearchBar placeholder="Ieškok pasiūlymų..." />
      </section>
      {/* Pasiūlymų skiltis — dviejų stulpelių tinklelis visame puslapyje */}
      <section className="px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl justify-cnter font-semibold mb-6">Pasiūlymai</h2>

          {/* Two-column responsive grid for deal slots */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="h-44 border rounded-lg bg-white/0" aria-hidden="true"></div>
            <div className="h-44 border rounded-lg bg-white/0" aria-hidden="true"></div>
            <div className="h-44 border rounded-lg bg-white/0" aria-hidden="true"></div>
            <div className="h-44 border rounded-lg bg-white/0" aria-hidden="true"></div>
            <div className="h-44 border rounded-lg bg-white/0" aria-hidden="true"></div>
            <div className="h-44 border rounded-lg bg-white/0" aria-hidden="true"></div>
          </div>
        </div>
      </section>

    </main>
  );
}