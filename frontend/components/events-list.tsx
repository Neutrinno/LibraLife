"use client"

import { useState } from "react"
import EventCard from "./event-card"
import RegistrationModal from "./registration-modal"

interface Event {
  id: number
  title: string
  type: string
  description: string
  date: string
  time: string
}

const events: Event[] = [
  {
    id: 1,
    title: "Литературные шарады",
    type: "Игра",
    description:
      "Интерактивная игра с загадками и шарадами на литературную тематику. Развивает внимательность и знание классической и современной литературы в веселой форме.",
    date: "24.11",
    time: "18:00",
  },
  {
    id: 2,
    title: "Путешествие в историю",
    type: "Лекция",
    description:
      "Увлекательное мероприятие-квест, погружающее участников в исторические события и становление государства. Познакомит с важными вехами прошлого, развивая знания и смекалку.",
    date: "25.11",
    time: "12:00",
  },
  {
    id: 3,
    title: "Проза и драма: исследование жанров",
    type: "Лекция",
    description:
      "Образовательное мероприятие, раскрывающее особенности и различия прозаических и драматических жанров в литературе. Помогает лучше понять структуру и выразительные средства каждого жанра.",
    date: "27.11",
    time: "19:00",
  },
  {
    id: 4,
    title: "Книжный клуб: Достоевский «Идиот»",
    type: "Обсуждение",
    description:
      "Занятие клуба, посвященное обсуждению романа «Идиот» Ф. Достоевского. Глубокий разбор сюжета, персонажей и философских идей произведения.",
    date: "28.11",
    time: "20:00",
  },
]

export default function EventsList() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null)

  const handleRegister = (event: Event) => {
    setSelectedEvent(event)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedEvent(null)
  }

  return (
    <>
      <div className="space-y-6">
        {events.map((event) => (
          <EventCard key={event.id} event={event} onRegister={handleRegister} />
        ))}
      </div>

      {selectedEvent && <RegistrationModal isOpen={isModalOpen} onClose={handleCloseModal} event={selectedEvent} />}
    </>
  )
}
