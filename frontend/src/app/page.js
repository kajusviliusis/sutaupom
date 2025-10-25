import Image from "next/image";
import Link from "next/link";
// import NavBar from "@/components/NavBar";
// import SearchBar from "@/components/SearchBar";

const BACKGROUND_IMAGE_PATH = "/darzoves.jpg";
const LOGO_IMAGE_PATH = "/sutaupom.png";

export const metadata = {
  title: 'SUTAUPOM - Pagrindinis',
};

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      {/* sita vieta pakeisti navbar komponentu */}
      <nav className="flex justify-end space-x-6 p-4 text-sm md:text-base font-medium text-black max-w-7xl mx-auto">
        <Link href="/" className="font-bold">Pagrindinis</Link>
        <Link href="/pasiulymai" className="hover:opacity-75">Pasiūlymai</Link>
        <Link href="/apie-mus" className="hover:opacity-75">Apie mus</Link>
      </nav>

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
            {/* sita vieta pakeisti searchbar komponentu*/}
            <div className="flex w-full max-w-xl bg-white rounded-full overflow-hidden shadow-lg">
              <input
                type="text"
                placeholder="Įveskite prekę..."
                className="flex-grow p-4 pl-6 text-gray-700 outline-none"
              />
              <button
                type="button"
                className="bg-gray-800 text-white font-semibold px-6 py-4 hover:bg-gray-700 transition"
              >
                Ieškoti
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
