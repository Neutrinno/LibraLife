import type React from "react"
import type { Metadata } from "next"
import { Mulish, Wix_Madefor_Display } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const mulish = Mulish({ subsets: ["latin", "cyrillic"], variable: "--font-mulish" })
const wixDisplay = Wix_Madefor_Display({ subsets: ["latin", "cyrillic"], variable: "--font-wix-display" })

export const metadata: Metadata = {
  title: "Библиотека №14 - Ваше пространство для новых открытий",
  description: "Библиотека №14 - современное пространство для развития. Книги, мероприятия и новые знания ждут вас!",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru">
      <body className={`${mulish.variable} ${wixDisplay.variable} font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
