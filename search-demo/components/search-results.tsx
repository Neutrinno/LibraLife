import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Calendar, MapPin } from "lucide-react"

interface SearchResult {
  id: string
  title: string
  type: "book" | "event"
  author?: string
  category?: string
  location?: string
  date?: string
  description?: string
}

interface SearchResultsProps {
  results: SearchResult[]
}

export function SearchResults({ results }: SearchResultsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {results.map((result) => (
        <Card key={result.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between gap-2 mb-2">
              <CardTitle className="text-lg leading-tight text-balance">{result.title}</CardTitle>
              {result.type === "book" ? (
                <BookOpen className="h-5 w-5 text-primary flex-shrink-0" />
              ) : (
                <Calendar className="h-5 w-5 text-primary flex-shrink-0" />
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">{result.type === "book" ? "Книга" : "Мероприятие"}</Badge>
              {result.category && <Badge variant="outline">{result.category}</Badge>}
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {result.author && (
              <p className="text-sm text-muted-foreground">
                <span className="font-medium">Автор:</span> {result.author}
              </p>
            )}
            {result.location && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{result.location}</span>
              </div>
            )}
            {result.date && (
              <p className="text-sm text-muted-foreground">
                <span className="font-medium">Дата:</span> {result.date}
              </p>
            )}
            {result.description && (
              <p className="text-sm text-foreground line-clamp-3 leading-relaxed">{result.description}</p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
