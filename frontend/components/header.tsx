"use client"

import Link from "next/link"
import { useState } from "react"

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link href="/" className="flex-shrink-0">
            <div className="border-2 border-orange-500 px-3 py-2" style={{ fontFamily: "var(--font-display-family)" }}>
              <div className="text-orange-500 font-bold text-sm md:text-base">Библиотека</div>
              <div className="text-orange-500 font-bold text-sm md:text-base">№14</div>
              <div className="text-gray-600 text-xs font-light leading-tight">пространство для развития</div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex gap-8 items-center">
            <Link href="/" className="text-gray-900 hover:text-orange-500 font-medium">
              Главная
            </Link>
            <Link href="/books" className="text-gray-900 hover:text-orange-500 font-medium">
              Книги
            </Link>
            <Link href="/events" className="text-gray-900 hover:text-orange-500 font-medium">
              Мероприятия
            </Link>
          </nav>

          <Link
            href="/profile"
            className="hidden md:block border-2 border-gray-900 px-4 py-2 text-gray-900 font-medium hover:bg-gray-50"
          >
            Профиль
          </Link>

          {/* Mobile Menu Button */}
          <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden pb-4 space-y-2">
            <Link href="/" className="block text-gray-900 hover:text-orange-500 font-medium py-2">
              Главная
            </Link>
            <Link href="/books" className="block text-gray-900 hover:text-orange-500 font-medium py-2">
              Книги
            </Link>
            <Link href="/events" className="block text-gray-900 hover:text-orange-500 font-medium py-2">
              Мероприятия
            </Link>
            <Link
              href="/profile"
              className="block w-full border-2 border-gray-900 px-4 py-2 text-gray-900 font-medium hover:bg-gray-50 mt-2 text-center"
            >
              Профиль
            </Link>
          </nav>
        )}
      </div>
    </header>
  )
}
