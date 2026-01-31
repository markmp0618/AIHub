import type { Metadata } from 'next';
import { Playfair_Display } from 'next/font/google';
import './globals.css';

// Display font - Playfair Display (elegant serif, GT Sectra alternative)
const displayFont = Playfair_Display({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-display',
  display: 'swap',
});

// Body font will use Pretendard Variable from globals.css

export const metadata: Metadata = {
  title: 'AIHub - AI를 실행으로 바꿉니다',
  description:
    'AIHub은 AI를 정보가 아니라 실행으로 바꾸는 혁신적인 플랫폼입니다.',
  keywords: ['AI', 'AIHub', '인공지능', '챗봇', 'AI 플랫폼'],
  authors: [{ name: 'AIHub Team' }],
  openGraph: {
    title: 'AIHub - AI를 실행으로 바꿉니다',
    description:
      'AIHub은 AI를 정보가 아니라 실행으로 바꾸는 혁신적인 플랫폼입니다.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${displayFont.variable}`}>
      <body className="antialiased" style={{ fontFamily: "'Pretendard Variable', sans-serif" }}>{children}</body>
    </html>
  );
}
