"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { BookRecommendations } from "./book-recommendations"
import { Sparkles } from "lucide-react"

export function RecommendationsSection() {
  const [bookId, setBookId] = useState<string>("")
  const [showRecommendations, setShowRecommendations] = useState(false)

  const handleGetRecommendations = () => {
    // For demo purposes, using a sample book ID
    // In production, this would come from user selection
    setBookId("sample-book-id")
    setShowRecommendations(true)
  }

  return (
    <section className="space-y-8">
      <div className="text-center max-w-2xl mx-auto space-y-4">
        <h2 className="text-2xl font-semibold">Рекомендации похожих книг</h2>
        <p className="text-muted-foreground leading-relaxed">
          Получите персонализированные рекомендации книг на основе ваших интересов
        </p>
        <Button onClick={handleGetRecommendations} size="lg" className="gap-2">
          <Sparkles className="h-5 w-5" />
          Получить рекомендации
        </Button>
      </div>

      {showRecommendations && <BookRecommendations bookId={bookId} />}
    </section>
  )
}
