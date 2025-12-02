"use client";
import Image from "next/image";
import NavBar from '../../components/NavBar.js';
import SearchBar from "../../components/SearchBar.js";

const BACKGROUND_IMAGE_PATH = "/darzoves.jpg";
const LOGO_IMAGE_PATH = "/sutaupom.png";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white flex flex-col min-h-screen">
      <NavBar />

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
            <Image
              src={LOGO_IMAGE_PATH}
              alt="SUTAUPOM logotipas"
              width={500}
              height={120}
              priority
              className="w-auto h-auto mb-10"
            />

            <SearchBar placeholder="Ieškok pasiūlymų..." />
          </div>
        </div>
      </section>

      <div className="w-[90%] mx-auto flex justify-end items-center mb-1">
        <Image 
          src="/Logo.png"
          alt="Mazas logo"
          width={90}
          height={40}
        />
      </div>
      <div className="w-[90%] mx-auto border-t border-gray-300 mt-1 mb-2"></div>
    </main>
  );
}
