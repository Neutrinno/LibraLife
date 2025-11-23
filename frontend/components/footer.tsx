export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 mb-8">
          {/* Logo & Address */}
          <div className="space-y-6">
            <div
              className="border-2 border-orange-500 inline-block px-3 py-2"
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              <div className="text-orange-500 font-bold text-sm">Библиотека №14</div>
              <div className="text-gray-600 text-xs font-light leading-tight">пространство для развития</div>
            </div>
            <div>
              <p className="text-gray-700 font-sans text-sm">
                г. Екатеринбург,
                <br />
                ул. Свердлова, 25
              </p>
            </div>
          </div>

          {/* Navigation & Hours */}
          <div className="space-y-6">
            <div style={{ fontFamily: "var(--font-display-family)" }}>
              <p className="font-bold text-gray-900 mb-2">Главная</p>
              <p className="font-bold text-gray-900 mb-2">Книги</p>
              <p className="font-bold text-gray-900 mb-4">Мероприятия</p>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-2" style={{ fontFamily: "var(--font-display-family)" }}>
                Часы работы
              </h4>
              <div className="text-gray-700 font-sans text-sm space-y-1">
                <div>
                  <span className="font-semibold">Будни</span> 10:00–20:00
                </div>
                <div>
                  <span className="font-semibold">Выходные</span> 10:00–18:00
                </div>
              </div>
            </div>
          </div>

          {/* Contacts & Decorative */}
          <div className="space-y-6">
            <div>
              <h4 className="font-bold text-gray-900 mb-2" style={{ fontFamily: "var(--font-display-family)" }}>
                Контакты
              </h4>
              <p className="text-gray-700 font-sans text-sm">+7 (343) 370–20–03</p>
            </div>
            {/* Decorative geometric pattern */}
            <div className="space-y-2">
              <div className="flex gap-2">
                <div className="w-6 h-6 border-2 border-orange-500"></div>
                <div className="w-6 h-6 border-2 border-blue-500"></div>
              </div>
              <div className="flex gap-2">
                <div className="w-6 h-6 border-2 border-blue-500"></div>
                <div className="w-6 h-6 border-2 border-orange-500"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-200 pt-8">
          <p className="text-gray-600 text-sm text-center font-sans">© 2025 Библиотека №14. Все права защищены.</p>
        </div>
      </div>
    </footer>
  )
}
