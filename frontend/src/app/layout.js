import './globals.css'; 
import { Inter } from 'next/font/google'; 
// Navbar component removed — using page-level navbar in `src/app/page.js`

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Svetaine',
  description: 'Next.js projektas',
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