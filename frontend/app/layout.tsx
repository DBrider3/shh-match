import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '소확행♥ - 소소하지만 확실한 행복한 만남',
  description: '커피 한 잔의 여유로 시작하는 따뜻한 만남. 소소하지만 확실한 행복을 찾아주는 소확행 매칭 서비스입니다.',
  keywords: ['소확행', '따뜻한 만남', '커피', '일상의 행복', '소소한 행복', '아늤한 만남'],
  authors: [{ name: '소확행' }],
  robots: 'noindex, nofollow',
  openGraph: {
    title: '소확행♥ - 소소하지만 확실한 행복한 만남',
    description: '커피 한 잔의 여유로 시작하는 따뜻한 만남',
    type: 'website',
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={`${inter.className} min-h-screen flex flex-col font-cozy`}>
        <Providers>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}