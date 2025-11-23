import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get("q") || "*"
  const page = searchParams.get("page") || "1"
  const perPage = searchParams.get("per_page") || "20"

  try {
    // Mock response for demonstration
    // Replace with actual API call: https://your-api-domain.com/api/search/
    const mockResults = [
      {
        id: "1",
        title: "Мастер и Маргарита",
        type: "book",
        author: "Михаил Булгаков",
        category: "Классическая литература",
        description: "Роман о дьяволе, который посещает атеистический СССР...",
      },
      {
        id: "2",
        title: "Литературная встреча",
        type: "event",
        location: "Библиотека им. Ленина",
        date: "2025-01-15",
        category: "Встреча с автором",
        description: "Встреча с современным писателем и обсуждение новой книги...",
      },
      {
        id: "3",
        title: "Война и мир",
        type: "book",
        author: "Лев Толстой",
        category: "Классическая литература",
        description: "Эпический роман о жизни русского общества в эпоху наполеоновских войн...",
      },
    ]

    const filteredResults =
      query === "*" ? mockResults : mockResults.filter((item) => item.title.toLowerCase().includes(query.toLowerCase()))

    return NextResponse.json({
      results: filteredResults,
      total: filteredResults.length,
      page: Number.parseInt(page),
      per_page: Number.parseInt(perPage),
    })
  } catch (error) {
    console.error("[v0] Search API error:", error)
    return NextResponse.json({ error: "Failed to fetch search results" }, { status: 500 })
  }
}
