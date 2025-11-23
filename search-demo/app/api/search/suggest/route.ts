import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get("q") || ""

  if (query.length < 2) {
    return NextResponse.json({ suggestions: [] })
  }

  try {
    // Mock response for demonstration
    // Replace with actual API call: https://your-api-domain.com/api/search/suggest
    const mockSuggestions = [
      { text: "Мастер и Маргарита", type: "book" as const },
      { text: "Война и мир", type: "book" as const },
      { text: "Литературная встреча", type: "event" as const },
      { text: "Преступление и наказание", type: "book" as const },
      { text: "Книжная ярмарка", type: "event" as const },
    ]

    const filteredSuggestions = mockSuggestions.filter((item) => item.text.toLowerCase().includes(query.toLowerCase()))

    return NextResponse.json({
      suggestions: filteredSuggestions.slice(0, 5),
    })
  } catch (error) {
    console.error("[v0] Suggest API error:", error)
    return NextResponse.json({ error: "Failed to fetch suggestions" }, { status: 500 })
  }
}
