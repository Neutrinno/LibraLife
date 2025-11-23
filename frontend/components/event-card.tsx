"use client"

interface Event {
  id: number
  title: string
  type: string
  description: string
  date: string
  time: string
}

interface EventCardProps {
  event: Event
  onRegister: (event: Event) => void
}

export default function EventCard({ event, onRegister }: EventCardProps) {
  return (
    <div className="border-l-4 border-orange-500 pl-6 py-6 relative">
      {/* Orange bracket styling */}
      <div className="absolute -left-3 top-0 w-6 h-6 border-l-2 border-t-2 border-orange-500"></div>
      <div className="absolute -left-3 bottom-0 w-6 h-6 border-l-2 border-b-2 border-orange-500"></div>
      <div className="absolute -right-3 top-0 w-6 h-6 border-r-2 border-t-2 border-orange-500"></div>
      <div className="absolute -right-3 bottom-0 w-6 h-6 border-r-2 border-b-2 border-orange-500"></div>

      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 md:gap-12">
        {/* Left content */}
        <div className="flex-1">
          <h3
            className="text-2xl md:text-3xl font-bold text-black mb-2"
            style={{ fontFamily: "var(--font-wix-display)" }}
          >
            {event.title}
          </h3>
          <p className="text-sm text-gray-600 mb-4 font-medium">{event.type}</p>
          <p className="text-gray-700 leading-relaxed text-sm md:text-base">{event.description}</p>
        </div>

        {/* Right content with date and button */}
        <div className="flex flex-col items-end justify-start gap-6 md:gap-8">
          <div className="text-right">
            <div className="text-3xl md:text-4xl font-bold text-black">{event.date}</div>
            <div className="text-lg md:text-xl text-gray-700 font-medium">{event.time}</div>
          </div>
          <button
            onClick={() => onRegister(event)}
            className="px-4 py-2 border border-black text-black font-medium hover:bg-black hover:text-white transition-colors text-sm md:text-base whitespace-nowrap"
            style={{ fontFamily: "var(--font-mulish)" }}
          >
            Зарегистрироваться
            <br />
            на мероприятие
          </button>
        </div>
      </div>
    </div>
  )
}
