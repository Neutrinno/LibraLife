"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Star } from "lucide-react"

interface Recommendation {
  id: string
  title: string
  author?: string
  category?: string
  similarity_score?: number
  description?: string
}

interface BookRecommendationsProps {
  bookId: string
}

export function BookRecommendations({ bookId }: BookRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchRecommendations = async () => {
      setIsLoading(true)
      try {
        const response = await fetch(`/api/recommendations/${bookId}`)
        const data = await response.json()
        setRecommendations(data.recommendations || [])
      } catch (error) {
        console.error("[v0] Recommendations error:", error)
        setRecommendations([])
      } finally {
        setIsLoading(false)
      }
    }

    if (bookId) {
      fetchRecommendations()
    }
  }, [bookId])

  if (isLoading) {
    return <div className="text-center text-muted-foreground py-8">Загрузка рекомендаций...</div>
  }

  if (recommendations.length === 0) {
    return <div className="text-center text-muted-foreground py-8">Рекомендации не найдены</div>
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-center">Похожие книги</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recommendations.map((book) => (
          <Card key={book.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center gap-3 mb-4">
                {/* Placeholder image */}
                <div className="w-16 h-24 bg-muted rounded-md flex items-center justify-center flex-shrink-0">
                  <BookOpen className="h-8 w-8 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-base leading-tight text-balance mb-2">{book.title}</CardTitle>
                  {book.author && <p className="text-xs text-muted-foreground truncate">{book.author}</p>}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {book.category && (
                  <Badge variant="secondary" className="text-xs">
                    {book.category}
                  </Badge>
                )}
                {book.similarity_score && (
                  <Badge variant="outline" className="text-xs gap-1">
                    <Star className="h-3 w-3 fill-current" />
                    {Math.round(book.similarity_score * 100)}%
                  </Badge>
                )}
              </div>
            </CardHeader>
            {book.description && (
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">{book.description}</p>
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  )
}
