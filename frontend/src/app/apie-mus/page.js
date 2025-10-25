// import NavBar from '@/components/NavBar'; 
import Link from "next/link";

export const metadata = {
    title: 'Apie Mus | SUTAUPOM',
};

export default function ApieMusPage() {
    return (
        <main className="min-h-screen bg-white">
            
            {/* sita vieta reikes pakeisti navbar komponentu*/}
            <div className="p-4 border-b border-gray-100">
                <div className="flex justify-end items-center max-w-7xl mx-auto text-sm md:text-base font-medium">
                    <Link href="/" className="ml-6 text-gray-600 hover:text-gray-900">Pagrindinis</Link>
                    <Link href="/pasiulymai" className="ml-6 text-gray-600 hover:text-gray-900">Pasiūlymai</Link>
                    <Link href="/apie-mus" className="ml-6 font-bold text-gray-900">Apie mus</Link>
                </div>
            </div>

            {/* centravimas */}
            <div className="flex flex-col items-center pt-10 pb-24 px-4 md:px-8">
                
                <h1 className="text-4xl md:text-5xl font-extrabold mb-12 mt-8 text-center">Apie mus:</h1>

                {/* blokas informacijos */}
                <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl p-8 md:p-12 border border-gray-100">

                    {/* tikslas ir vizija grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 mb-12 text-gray-700">
                        
                        {/* tikslo blokas */}
                        <div className="space-y-3">
                            <div className="flex items-center space-x-3">
                                <span className="text-2xl text-red-600 font-extrabold">◉</span>
                                <h2 className="text-xl font-bold text-gray-900">Mūsų tikslas:</h2>
                            </div>
                            <p className="text-md pl-8">
                                Padėti žmonėms, ypatingai studentams, sutaupyti pinigų!
                            </p>
                        </div>

                        {/* vizijos blokas */}
                        <div className="space-y-3">
                            <div className="flex items-center space-x-3">
                                <span className="text-2xl text-red-600 font-extrabold">👁️</span>
                                <h2 className="text-xl font-bold text-gray-900">Vizija:</h2>
                            </div>
                            <p className="text-md pl-8">
                                Lietuvą paversti ekonomiškai pirmaujančia pasaulio valstybe!
                            </p>
                        </div>
                    </div>

                    {/* kontaktai */}
                    <h3 className="text-2xl font-bold text-center mt-12 mb-8 text-gray-900 border-t pt-8">
                        Susisiekite su mūsų komanda:
                    </h3>

                    <div className="flex flex-col md:flex-row justify-around items-center space-y-6 md:space-y-0 text-gray-700">
                        <div className="flex items-center space-x-3">
                            <span className="text-2xl text-gray-700">📞</span>
                            <p className="text-lg font-medium">+370********</p>
                        </div>
                        <div className="flex items-center space-x-3">
                            <span className="text-2xl text-gray-700">📧</span>
                            <p className="text-lg font-medium">Kontaktai@Sutaupom.lt</p>
                        </div>
                    </div>

                </div>
            </div>
            
        </main>
    );
}