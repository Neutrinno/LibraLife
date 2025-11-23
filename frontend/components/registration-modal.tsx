"use client"

import type React from "react"

import { useState } from "react"
import { X } from "lucide-react"

interface Event {
  id: number
  title: string
  type: string
  description: string
  date: string
  time: string
}

interface RegistrationModalProps {
  isOpen: boolean
  onClose: () => void
  event: Event
}

export default function RegistrationModal({ isOpen, onClose, event }: RegistrationModalProps) {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState("")

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate form submission
    setTimeout(() => {
      setSubmitMessage("Спасибо! Вы успешно зарегистрировались на мероприятие.")
      setFormData({ firstName: "", lastName: "", email: "" })
      setIsSubmitting(false)

      // Close modal after 2 seconds
      setTimeout(() => {
        onClose()
        setSubmitMessage("")
      }, 2000)
    }, 500)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-black" style={{ fontFamily: "var(--font-wix-display)" }}>
              Регистрация
            </h2>
            <p className="text-sm text-gray-600 mt-1">{event.title}</p>
            <p className="text-xs text-gray-500 mt-0.5">
              {event.date} в {event.time}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {submitMessage ? (
            <div className="text-center py-8">
              <p className="text-green-600 font-medium">{submitMessage}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* First Name */}
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
                  Имя
                </label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="Иван"
                />
              </div>

              {/* Last Name */}
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
                  Фамилия
                </label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="Иванов"
                />
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  placeholder="ivan@example.com"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full mt-6 px-4 py-2 bg-orange-500 text-white font-medium rounded-md hover:bg-orange-600 disabled:opacity-50 transition-colors"
              >
                {isSubmitting ? "Регистрация..." : "Зарегистрироваться"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
