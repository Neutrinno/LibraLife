export default function Knowledge() {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
      <div className="flex items-center gap-2 mb-8">
        <span className="text-blue-500 text-4xl md:text-5xl font-bold">⦗</span>
        <h2
          className="text-3xl md:text-4xl font-bold text-gray-900"
          style={{ fontFamily: "var(--font-display-family)" }}
        >
          Открой дверь в новые знания
        </h2>
        <span className="text-blue-500 text-4xl md:text-5xl font-bold">⦘</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
        {/* Search Section */}
        <div className="md:col-span-2">
          <input
            type="text"
            placeholder="Найти книги и мероприятия"
            className="w-full px-4 py-3 border-2 border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button className="mt-4 border-2 border-gray-900 px-6 py-2 text-gray-900 font-medium hover:bg-gray-50">
            [Поиск]
          </button>
        </div>
      </div>
    </section>
  )
}
