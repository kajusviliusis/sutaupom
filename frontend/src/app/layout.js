
import './globals.css'; 
import { Inter } from 'next/font/google'; 

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'SUTAUPOM - Pagrindinis',
  description: 'Parduotuvė, kurioje galima sutaupyti.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="lt">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}