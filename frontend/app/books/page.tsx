import Header from "@/components/header"
import BracketFrame from "@/components/bracket-frame"
import Footer from "@/components/footer"

export default function BooksPage() {
  const books = [
    {
      id: 1,
      title: "Подходим друг другу",
      authors: "Амир Левин, Рэйчел Хеллер",
      status: "На рухах",
      statusColor: "orange",
      image: "/book-cover-turquoise-pink-friendship.jpg",
    },
    {
      id: 2,
      title: "О детях Кащеевых",
      authors: "Алёна Селютина",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-flower-ornate-design.jpg",
    },
    {
      id: 3,
      title: "Легенды гор и морей. Монстры и предания Древнего Китая",
      authors: "Электра Яншина",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-dark-red-mythical-creatures.jpg",
    },
    {
      id: 4,
      title: "Вечера в книжном морисаки",
      authors: "Сатоси Ягисава",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-purple-bookstore-night.jpg",
    },
    {
      id: 5,
      title: "Чёрная изба",
      authors: "Наталия Колимакова, Наталья Матушмачи, Анна Лунева",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-dark-blue-fairy-tale.jpg",
    },
    {
      id: 6,
      title: "Обыкновенное чудо",
      authors: "Евгений Шварц",
      status: "На рухах",
      statusColor: "orange",
      image: "/book-cover-portrait-illustration-magic.jpg",
    },
    {
      id: 7,
      title: "Нити ярче серебра",
      authors: "Кика Хатзополу",
      status: "На рухах",
      statusColor: "orange",
      image: "/book-cover-colorful-spiral-fantasy.jpg",
    },
    {
      id: 8,
      title: "Ментальная перезагрузка. 5 шагов к своей настоящей жизни",
      authors: "Эрик Ларссен",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-self-help-minimalist-man.jpg",
    },
    {
      id: 9,
      title: "Калевала",
      authors: "Перевод Леонида Бельского",
      status: "На рухах",
      statusColor: "orange",
      image: "/book-cover-dark-teal-folklore-ornaments.jpg",
    },
    {
      id: 10,
      title: "О детях Кащеевых",
      authors: "Борис Пастернак",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-elegant-white-script.jpg",
    },
    {
      id: 11,
      title: "Грозовой перевал. Графический роман",
      authors: "Ян, Эдит",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-dark-gothic-woman-storm.jpg",
    },
    {
      id: 12,
      title: "Последователи",
      authors: "Иса Бель",
      status: "Свободна",
      statusColor: "blue",
      image: "/book-cover-white-red-roses-followers.jpg",
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Title */}
        <BracketFrame color="orange" size="large" position="top-right">
          <h1 className="text-4xl md:text-5xl font-bold" style={{ fontFamily: "var(--font-display-family)" }}>
            КНИГИ
          </h1>
        </BracketFrame>

        {/* Books Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
          {books.map((book) => (
            <div key={book.id} className="flex flex-col">
              {/* Book Cover */}
              <img
                src={book.image || "/placeholder.svg"}
                alt={book.title}
                className="w-full h-64 object-cover bg-gray-200 rounded"
              />

              {/* Book Info */}
              <div className="mt-4 flex-1">
                <h3 className="font-bold text-sm md:text-base text-gray-900 line-clamp-2">{book.title}</h3>
                <p className="text-xs md:text-sm text-gray-600 mt-1">{book.authors}</p>
              </div>

              {/* Status */}
              <div className="mt-3">
                <BracketFrame color={book.statusColor} size="small">
                  <span
                    className="text-xs md:text-sm font-medium"
                    style={{
                      color: book.statusColor === "orange" ? "#ff8c42" : "#4a6fa5",
                    }}
                  >
                    {book.status}
                  </span>
                </BracketFrame>
              </div>
            </div>
          ))}
        </div>

        {/* Show More Button */}
        <div className="flex justify-center mt-16">
          <BracketFrame color="orange" size="large" position="bottom">
            <button className="px-8 py-3 text-lg font-bold text-gray-900 hover:bg-orange-50">ПОКАЗАТЬ ЕЩЁ</button>
          </BracketFrame>
        </div>
      </main>

      <Footer />
    </div>
  )
}
