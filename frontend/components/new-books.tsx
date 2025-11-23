export default function NewBooks() {
  const books = [
    {
      title: "Подходим друг другу",
      author: "Амир Левин, Рэйчел Хеллер",
      color: "bg-teal-500",
    },
    {
      title: "О детях Кощеевых",
      author: "Алёна Селютина",
      color: "bg-orange-100",
    },
    {
      title: "Легенды гор и морей",
      author: "Монстры и предания Древнего Китая. Электра Яншина",
      color: "bg-gray-800",
    },
    {
      title: "Вечера в книжном",
      author: "Сатоси Ягисава",
      color: "bg-purple-700",
    },
  ]

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
      <div className="flex items-center gap-2 mb-8">
        <span className="text-orange-500 text-4xl md:text-5xl font-bold">⦗</span>
        <h2
          className="text-3xl md:text-4xl font-bold text-gray-900"
          style={{ fontFamily: "var(--font-display-family)" }}
        >
          Новинки
        </h2>
        <span className="text-orange-500 text-4xl md:text-5xl font-bold">⦘</span>
        <button className="ml-auto border-2 border-gray-900 px-4 py-2 text-gray-900 font-medium hover:bg-gray-50 text-sm">
          [Показать всё]
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        {books.map((book, index) => (
          <div key={index} className="space-y-3">
            <div className={`${book.color} h-48 md:h-64 rounded-lg`} />
            <h3
              className="font-bold text-gray-900 text-sm md:text-base"
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              {book.title}
            </h3>
            <p className="text-gray-600 text-xs md:text-sm font-sans">{book.author}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
