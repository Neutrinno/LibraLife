"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { createEvent, updateEvent } from "@/lib/api"
import type { Event, EventCreate, EventUpdate } from "@/lib/types"
import { Loader2 } from "lucide-react"

interface EventDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  event?: Event | null
  onSuccess: () => void
}

export function EventDialog({ open, onOpenChange, event, onSuccess }: EventDialogProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    date: "",
    location: "",
    participants_count: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    if (event) {
      setFormData({
        title: event.title,
        description: event.description || "",
        date: event.date,
        location: event.location || "",
        participants_count: event.participants_count?.toString() || "",
      })
    } else {
      setFormData({
        title: "",
        description: "",
        date: "",
        location: "",
        participants_count: "",
      })
    }
  }, [event, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const eventData = {
        title: formData.title,
        description: formData.description || undefined,
        date: formData.date,
        location: formData.location || undefined,
        participants_count: formData.participants_count ? Number.parseInt(formData.participants_count) : undefined,
      }

      if (event) {
        await updateEvent(event.id, eventData as EventUpdate)
        toast({
          title: "Успешно",
          description: "Мероприятие обновлено",
        })
      } else {
        await createEvent(eventData as EventCreate)
        toast({
          title: "Успешно",
          description: "Мероприятие создано",
        })
      }

      onSuccess()
    } catch (error) {
      toast({
        title: "Ошибка",
        description: event ? "Не удалось обновить мероприятие" : "Не удалось создать мероприятие",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{event ? "Редактировать мероприятие" : "Добавить мероприятие"}</DialogTitle>
          <DialogDescription>
            {event ? "Измените информацию о мероприятии" : "Заполните информацию о новом мероприятии"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">
              Название <span className="text-destructive">*</span>
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              placeholder="Встреча книжного клуба"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Описание</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Описание мероприятия..."
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="date">
              Дата и время <span className="text-destructive">*</span>
            </Label>
            <Input
              id="date"
              type="datetime-local"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">Место проведения</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="Библиотека им. Пушкина"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="participants_count">Вместимость (количество мест)</Label>
            <Input
              id="participants_count"
              type="number"
              min="1"
              value={formData.participants_count}
              onChange={(e) => setFormData({ ...formData, participants_count: e.target.value })}
              placeholder="100"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Отмена
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-primary hover:bg-primary/90">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {event ? "Сохранить" : "Создать"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
