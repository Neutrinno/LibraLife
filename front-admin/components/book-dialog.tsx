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
import { createBook, updateBook } from "@/lib/api"
import type { Book, BookCreate, BookUpdate } from "@/lib/types"
import { Loader2 } from "lucide-react"

interface BookDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  book?: Book | null
  onSuccess: () => void
}

export function BookDialog({ open, onOpenChange, book, onSuccess }: BookDialogProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    description: "",
    isbn: "",
    published_year: "",
    cover_url: "",
    tags: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    if (book) {
      setFormData({
        title: book.title,
        author: book.author,
        description: book.description || "",
        isbn: book.isbn || "",
        published_year: book.published_year?.toString() || "",
        cover_url: book.cover_url || "",
        tags: book.tags?.join(", ") || "",
      })
    } else {
      setFormData({
        title: "",
        author: "",
        description: "",
        isbn: "",
        published_year: "",
        cover_url: "",
        tags: "",
      })
    }
  }, [book, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const tags = formData.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0)

      const bookData = {
        title: formData.title,
        author: formData.author,
        description: formData.description || undefined,
        isbn: formData.isbn || undefined,
        published_year: formData.published_year ? Number.parseInt(formData.published_year) : undefined,
        cover_url: formData.cover_url || undefined,
        tags: tags.length > 0 ? tags : undefined,
      }

      if (book) {
        await updateBook(book.id, bookData as BookUpdate)
        toast({
          title: "Успешно",
          description: "Книга обновлена",
        })
      } else {
        await createBook(bookData as BookCreate)
        toast({
          title: "Успешно",
          description: "Книга создана",
        })
      }

      onSuccess()
    } catch (error) {
      toast({
        title: "Ошибка",
        description: book ? "Не удалось обновить книгу" : "Не удалось создать книгу",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{book ? "Редактировать книгу" : "Добавить книгу"}</DialogTitle>
          <DialogDescription>
            {book ? "Измените информацию о книге" : "Заполните информацию о новой книге"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="title">
                Название <span className="text-destructive">*</span>
              </Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                placeholder="Война и мир"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="author">
                Автор <span className="text-destructive">*</span>
              </Label>
              <Input
                id="author"
                value={formData.author}
                onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                required
                placeholder="Лев Толстой"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Описание</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Краткое описание книги..."
              rows={4}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="isbn">ISBN</Label>
              <Input
                id="isbn"
                value={formData.isbn}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                placeholder="978-5-17-083851-3"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="published_year">Год издания</Label>
              <Input
                id="published_year"
                type="number"
                value={formData.published_year}
                onChange={(e) => setFormData({ ...formData, published_year: e.target.value })}
                placeholder="2024"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="cover_url">URL обложки</Label>
            <Input
              id="cover_url"
              type="url"
              value={formData.cover_url}
              onChange={(e) => setFormData({ ...formData, cover_url: e.target.value })}
              placeholder="https://example.com/cover.jpg"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="tags">Теги</Label>
            <Input
              id="tags"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="классика, роман, история (через запятую)"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Отмена
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-primary hover:bg-primary/90">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {book ? "Сохранить" : "Создать"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
