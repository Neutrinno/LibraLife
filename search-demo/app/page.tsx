import { SearchSection } from "@/components/search-section"
import { RecommendationsSection } from "@/components/recommendations-section"

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-balance">LibraLife</h1>
          <p className="text-muted-foreground text-lg">Интеллектуальный поиск книг и мероприятий</p>
        </header>

        {/* Search Section */}
        <SearchSection />

        {/* Divider */}
        <div className="my-16 border-t border-border" />

        {/* Recommendations Section */}
        <RecommendationsSection />
      </div>
    </main>
  )
}
