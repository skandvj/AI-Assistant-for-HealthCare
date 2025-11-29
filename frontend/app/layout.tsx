import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Premium Dental Care - Chatbot',
  description: 'Intelligent dental practice assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

