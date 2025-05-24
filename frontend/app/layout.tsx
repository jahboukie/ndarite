import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/providers/theme-provider'
import { ToastProvider } from '@/components/providers/toast-provider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NDARite - Legal NDA Generation Platform',
  description: 'Generate legally-compliant, industry-specific Non-Disclosure Agreements through an intelligent questionnaire system.',
  keywords: 'NDA, Non-Disclosure Agreement, Legal Documents, Contract Generation, Legal Tech',
  authors: [{ name: 'NDARite Team' }],
  creator: 'NDARite',
  publisher: 'NDARite',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'NDARite - Legal NDA Generation Platform',
    description: 'Generate legally-compliant, industry-specific Non-Disclosure Agreements through an intelligent questionnaire system.',
    url: '/',
    siteName: 'NDARite',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'NDARite - Legal NDA Generation Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'NDARite - Legal NDA Generation Platform',
    description: 'Generate legally-compliant, industry-specific Non-Disclosure Agreements through an intelligent questionnaire system.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
      </head>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <div className="relative flex min-h-screen flex-col">
            <div className="flex-1">
              {children}
            </div>
          </div>
          <ToastProvider />
        </ThemeProvider>
      </body>
    </html>
  )
}
