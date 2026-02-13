import type { Metadata } from 'next';
import { Space_Grotesk, Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

// Bitcoin DeFi Typography System
const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Microbial Segmentation | Temporal Analysis Platform',
  description: 'Advanced temporal segmentation of microbial time-lapse videos using deep learning. Analyze cell growth, phenotypes, and division events with precision.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-void antialiased">
        {/* Ambient Background Effects */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          {/* Radial Blur Background - Orange Glow */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-burnt-orange opacity-10 blur-[120px] rounded-full" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-bitcoin-orange opacity-10 blur-[150px] rounded-full" />
          
          {/* Grid Pattern Overlay */}
          <div className="absolute inset-0 bg-grid-pattern opacity-50" />
        </div>
        
        {children}
      </body>
    </html>
  );
}
