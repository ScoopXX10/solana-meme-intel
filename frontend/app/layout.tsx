import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Solana Meme Intel',
  description: 'Solana meme token scoring and intelligence dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background">
            <header className="border-b border-border">
              <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">🧠</span>
                    <h1 className="text-xl font-bold">Solana Meme Intel</h1>
                  </div>
                  <nav className="flex items-center space-x-4">
                    <a href="/" className="text-sm hover:text-primary">Dashboard</a>
                    <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground">
                      GitHub
                    </a>
                  </nav>
                </div>
              </div>
            </header>
            <main>{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
