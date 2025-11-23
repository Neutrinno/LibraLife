export default function Events() {
  const events = [
    {
      date: "24.11",
      time: "18:00",
      category: "Игра",
      title: "Литературные Шарады",
    },
    {
      date: "25.11",
      time: "12:00",
      category: "Лекция",
      title: "Путешествие в историю",
    },
    {
      date: "24.11",
      time: "18:00",
      category: "Лекция",
      title: "Проза и драма: Исследование жанров",
    },
    {
      date: "24.11",
      time: "18:00",
      category: "Обсуждение",
      title: "Книжный клуб: Ф. Достоевский «Идиот»",
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
          Мероприятия
        </h2>
        <span className="text-orange-500 text-4xl md:text-5xl font-bold">⦘</span>
        <button className="ml-auto border-2 border-gray-900 px-4 py-2 text-gray-900 font-medium hover:bg-gray-50 text-sm">
          [Показать всё]
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        {events.map((event, index) => (
          <div key={index} className="border-4 border-orange-500 p-6 hover:shadow-lg transition-shadow">
            <div
              className="text-orange-500 font-bold text-lg mb-4"
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              <div>{event.date}</div>
              <div>{event.time}</div>
            </div>
            <div className="space-y-3">
              <p className="text-gray-600 text-xs font-sans font-semibold uppercase">{event.category}</p>
              <h3 className="font-bold text-gray-900 text-sm" style={{ fontFamily: "var(--font-display-family)" }}>
                {event.title}
              </h3>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
