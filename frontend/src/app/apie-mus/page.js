import NavBar from '../../../components/NavBar.js';

export const metadata = {
    title: 'Apie Mus | SUTAUPOM',
};

export default function ApieMusPage() {
    return (
        <main className="min-h-screen bg-white">
            
            <NavBar />

            <div className="flex flex-col items-center pt-10 pb-24 px-4 md:px-8">
                
                <h1 className="text-4xl md:text-5xl font-extrabold mb-12 mt-8 text-center">Apie mus:</h1>

                <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl p-8 md:p-12 border border-gray-100">

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 mb-12 text-gray-700">

                        <div className="space-y-3">
                            <div className="flex items-center space-x-3">
                                <svg className="w-8 h-8 text-red-600" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" opacity="0.15" />
                                    <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" />
                                    <circle cx="12" cy="12" r="2" fill="currentColor" />
                                </svg>
                                <h2 className="text-xl font-bold text-gray-900">Mūsų tikslas:</h2>
                            </div>
                            <p className="text-md pl-10">
                                Padėti žmonėms, ypatingai studentams, sutaupyti pinigų!
                            </p>
                        </div>

                        <div className="space-y-3">
                            <div className="flex items-center space-x-3">
                                <svg className="w-8 h-8 text-red-600" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                    <path d="M12 4C7 4 4 8 4 12s3 8 8 8 8-4 8-8-3-8-8-8z" stroke="currentColor" strokeWidth="2" fill="none" />
                                    <circle cx="12" cy="12" r="2" fill="currentColor" />
                                </svg>
                                <h2 className="text-xl font-bold text-gray-900">Vizija:</h2>
                            </div>
                            <p className="text-md pl-10">
                                Lietuvą paversti ekonomiškai pirmaujančia pasaulio valstybe!
                            </p>
                        </div>
                    </div>

                    <h3 className="text-2xl font-bold text-center mt-12 mb-8 text-gray-900 border-t pt-8">
                        Susisiekite su mūsų komanda:
                    </h3>

                    <div className="flex flex-col md:flex-row justify-around items-center space-y-6 md:space-y-0 text-gray-700">
                        <div className="flex items-center space-x-3">
                            <svg className="w-6 h-6 text-gray-700" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                <path d="M22 16.92V21a1 1 0 0 1-1.11 1 19 19 0 0 1-8.63-3.22 19 19 0 0 1-6-6A19 19 0 0 1 2 3.11 1 1 0 0 1 3 2h4.09a1 1 0 0 1 1 .75c.12.7.33 1.38.63 2.02a1 1 0 0 1-.24 1.02L7.5 8.5a16 16 0 0 0 6 6l1.7-1.98a1 1 0 0 1 1.02-.24c.64.3 1.32.51 2.02.63a1 1 0 0 1 .75 1V21z" stroke="currentColor" strokeWidth="1" fill="none" />
                            </svg>
                            <p className="text-lg font-medium">+370********</p>
                        </div>
                        <div className="flex items-center space-x-3">
                            <svg className="w-6 h-6 text-gray-700" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                                <path d="M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" stroke="currentColor" strokeWidth="1" fill="none" />
                                <path d="M3 7l9 6 9-6" stroke="currentColor" strokeWidth="1" fill="none" />
                            </svg>
                            <p className="text-lg font-medium">Kontaktai@Sutaupom.lt</p>
                        </div>
                    </div>

                </div>
            </div>
            
        </main>
    );
}