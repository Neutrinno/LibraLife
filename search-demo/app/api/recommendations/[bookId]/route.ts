import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest, { params }: { params: Promise<{ bookId: string }> }) {
  const { bookId } = await params

  try {
    // Mock response for demonstration
    // Replace with actual API call: https://your-api-domain.com/api/recommendations/{bookId}
    const mockRecommendations = [
      {
        id: "101",
        title: "Двенадцать стульев",
        author: "Илья Ильф, Евгений Петров",
        category: "Сатира",
        similarity_score: 0.89,
        description: "Сатирический роман о поисках сокровищ в послереволюционной России...",
      },
      {
        id: "102",
        title: "Собачье сердце",
        author: "Михаил Булгаков",
        category: "Сатира",
        similarity_score: 0.85,
        description: "Повесть о профессоре, который превращает собаку в человека...",
      },
      {
        id: "103",
        title: "Белая гвардия",
        author: "Михаил Булгаков",
        category: "Историческая проза",
        similarity_score: 0.82,
        description: "Роман о судьбе семьи русских интеллигентов в годы Гражданской войны...",
      },
      {
        id: "104",
        title: "Записки юного врача",
        author: "Михаил Булгаков",
        category: "Автобиографическая проза",
        similarity_score: 0.78,
        description: "Цикл рассказов о молодом враче, работающем в сельской больнице...",
      },
      {
        id: "105",
        title: "Театральный роман",
        author: "Михаил Булгаков",
        category: "Сатира",
        similarity_score: 0.75,
        description: "Роман о театре и творческом процессе создания спектакля...",
      },
      {
        id: "106",
        title: "Дни Турбиных",
        author: "Михаил Булгаков",
        category: "Драматургия",
        similarity_score: 0.72,
        description: "Пьеса о судьбах интеллигенции в революционное время...",
      },
    ]

    return NextResponse.json({
      recommendations: mockRecommendations,
      book_id: bookId,
    })
  } catch (error) {
    console.error("[v0] Recommendations API error:", error)
    return NextResponse.json({ error: "Failed to fetch recommendations" }, { status: 500 })
  }
}
