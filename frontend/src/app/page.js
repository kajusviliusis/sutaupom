"use client";
import Image from "next/image";
import NavBar from '../../components/NavBar.js';
// import NavBar from "@/components/NavBar";
import SearchBar from "../../components/SearchBar.js";

const BACKGROUND_IMAGE_PATH = "/darzoves.jpg";
const LOGO_IMAGE_PATH = "/sutaupom.png";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">

      <NavBar />

      {/* Centrinis blokas su fonu */}
      <section className="flex flex-col items-center justify-center h-[calc(100vh-6rem)] px-4">
        <div className="relative w-full max-w-5xl h-[600px] rounded-3xl shadow-2xl overflow-hidden">
          <Image
            src={BACKGROUND_IMAGE_PATH}
            alt="Fono daržovės"
            fill
            className="object-cover brightness-110 opacity-40"
            priority
          />

          <div className="relative z-10 flex flex-col items-center justify-center h-full p-8">
            {/* Logotipas */}
            <Image
              src={LOGO_IMAGE_PATH}
              alt="SUTAUPOM logotipas"
              width={500}
              height={120}
              priority
              className="w-auto h-auto mb-10"
            />

            {/* Paieska */}
            <SearchBar placeholder="Ieškok pasiūlymų..." />
          </div>
        </div>
      </section>
    </main>
  );
}
