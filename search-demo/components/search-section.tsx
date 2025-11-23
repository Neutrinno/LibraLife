"use client"

import { useState } from "react"
import { SearchInput } from "./search-input"
import { SearchResults } from "./search-results"

export function SearchSection() {
  const [results, setResults] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setResults([])
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)
      const data = await response.json()
      setResults(data.results || [])
    } catch (error) {
      console.error("[v0] Search error:", error)
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="space-y-8">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-semibold mb-6 text-center">Найдите книги и мероприятия</h2>
        <SearchInput onSearch={handleSearch} />
      </div>

      {isLoading && <div className="text-center text-muted-foreground">Поиск...</div>}

      {!isLoading && results.length > 0 && <SearchResults results={results} />}

      {!isLoading && results.length === 0 && (
        <div className="text-center text-muted-foreground">Начните поиск, чтобы увидеть результаты</div>
      )}
    </section>
  )
}
