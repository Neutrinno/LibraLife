"use client"

import Image from "next/image"

export default function Hero() {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 items-center">
        {/* Left Content */}
        <div>
          {/* Title with orange brackets */}
          <div className="flex items-start gap-2 mb-8">
            <span className="text-orange-500 text-4xl md:text-5xl font-bold">⦗</span>
            <h1
              className="text-4xl md:text-5xl font-bold text-gray-900 text-balance"
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              Ваше пространство для новых открытий
            </h1>
            <span className="text-orange-500 text-4xl md:text-5xl font-bold mt-2">⦘</span>
          </div>

          {/* Info Section */}
          <div className="space-y-6 mt-12">
            <div>
              <h3 className="text-gray-900 font-bold text-lg mb-2" style={{ fontFamily: "var(--font-display-family)" }}>
                Адрес
              </h3>
              <p className="text-gray-700 font-sans">
                г. Екатеринбург,
                <br />
                ул. Свердлова, 25
              </p>
            </div>
            <div>
              <h3 className="text-gray-900 font-bold text-lg mb-2" style={{ fontFamily: "var(--font-display-family)" }}>
                Часы работы
              </h3>
              <div className="text-gray-700 font-sans space-y-1">
                <div>
                  <span className="font-semibold">Будни</span> 10:00–20:00
                </div>
                <div>
                  <span className="font-semibold">Выходные</span> 10:00–18:00
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Content - Image */}
        <div className="flex justify-center md:justify-end">
          <div className="border-4 border-orange-500 overflow-hidden">
            <Image
              src="/images/d0-b3-d0-bb-d0-b0-d0-b2-d0-bd-d0-b0-d1-8f.jpg"
              alt="Библиотека №14 - интерьер"
              className="w-full h-auto max-w-sm object-cover"
              width={400}
              height={400}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
