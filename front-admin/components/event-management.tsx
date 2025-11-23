"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Plus, Pencil, Trash2, CalendarIcon, MapPin, Download, Users } from "lucide-react"
import { EventDialog } from "@/components/event-dialog"
import { useToast } from "@/hooks/use-toast"
import { deleteEvent, getEvents, downloadEventPassport } from "@/lib/api"
import type { Event } from "@/lib/types"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

export function EventManagement() {
  const [events, setEvents] = useState<Event[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingEvent, setEditingEvent] = useState<Event | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [eventToDelete, setEventToDelete] = useState<string | null>(null)
  const { toast } = useToast()

  const loadEvents = async () => {
    try {
      setIsLoading(true)
      const data = await getEvents()
      setEvents(data.events || [])
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось загрузить мероприятия",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadPassport = async (event: Event) => {
    try {
      const blob = await downloadEventPassport(event.id)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `паспорт_мероприятия_${event.id}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast({
        title: "Успешно",
        description: "Паспорт мероприятия загружен",
      })
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось скачать паспорт мероприятия",
        variant: "destructive",
      })
    }
  }

  useEffect(() => {
    loadEvents()
  }, [])

  const handleEdit = (event: Event) => {
    setEditingEvent(event)
    setDialogOpen(true)
  }

  const handleDelete = async () => {
    if (!eventToDelete) return

    try {
      await deleteEvent(eventToDelete)
      toast({
        title: "Успешно",
        description: "Мероприятие удалено",
      })
      loadEvents()
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось удалить мероприятие",
        variant: "destructive",
      })
    } finally {
      setDeleteDialogOpen(false)
      setEventToDelete(null)
    }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
    setEditingEvent(null)
  }

  const handleSuccess = () => {
    loadEvents()
    handleDialogClose()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("ru-RU", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Управление мероприятиями</h2>
          <p className="text-muted-foreground mt-1">Создавайте и редактируйте события для читателей</p>
        </div>
        <Button onClick={() => setDialogOpen(true)} className="bg-primary hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Добавить мероприятие
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded" />
                <div className="h-4 bg-muted rounded w-2/3 mt-2" />
              </CardHeader>
              <CardContent>
                <div className="h-4 bg-muted rounded w-full" />
                <div className="h-4 bg-muted rounded w-3/4 mt-2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : events.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <CalendarIcon className="h-16 w-16 text-muted-foreground mb-4" />
            <p className="text-lg font-medium text-foreground">Нет мероприятий</p>
            <p className="text-muted-foreground mb-6">Создайте первое мероприятие</p>
            <Button onClick={() => setDialogOpen(true)} className="bg-secondary hover:bg-secondary/90">
              <Plus className="mr-2 h-4 w-4" />
              Добавить мероприятие
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {events.map((event) => (
            <Card key={event.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg text-balance">{event.title}</CardTitle>
                <CardDescription className="flex items-center gap-1 mt-2">
                  <CalendarIcon className="h-4 w-4" />
                  {formatDate(event.date)}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-3 mb-4">{event.description}</p>
                {event.location && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <MapPin className="h-4 w-4" />
                    <span>{event.location}</span>
                  </div>
                )}
                {event.participants_count && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <Users className="h-4 w-4" />
                    <span>Вместимость: {event.participants_count} мест</span>
                  </div>
                )}
                <div className="flex flex-col gap-2 mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadPassport(event)}
                    className="w-full bg-accent hover:bg-accent/90"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Скачать паспорт мероприятия
                  </Button>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleEdit(event)} className="flex-1">
                      <Pencil className="mr-2 h-4 w-4" />
                      Изменить
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => {
                        setEventToDelete(event.id)
                        setDeleteDialogOpen(true)
                      }}
                      className="flex-1"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Удалить
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <EventDialog open={dialogOpen} onOpenChange={handleDialogClose} event={editingEvent} onSuccess={handleSuccess} />

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Вы уверены?</AlertDialogTitle>
            <AlertDialogDescription>
              Это действие нельзя отменить. Мероприятие будет удалено безвозвратно.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Отмена</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Удалить
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
