"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Plus, Pencil, Trash2, BookOpen } from "lucide-react"
import { BookDialog } from "@/components/book-dialog"
import { useToast } from "@/hooks/use-toast"
import { deleteBook, getBooks } from "@/lib/api"
import type { Book } from "@/lib/types"
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
import { Badge } from "@/components/ui/badge"

export function BookManagement() {
  const [books, setBooks] = useState<Book[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingBook, setEditingBook] = useState<Book | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [bookToDelete, setBookToDelete] = useState<string | null>(null)
  const { toast } = useToast()

  const loadBooks = async () => {
    try {
      setIsLoading(true)
      const data = await getBooks()
      setBooks(data.books || [])
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось загрузить книги",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadBooks()
  }, [])

  const handleEdit = (book: Book) => {
    setEditingBook(book)
    setDialogOpen(true)
  }

  const handleDelete = async () => {
    if (!bookToDelete) return

    try {
      await deleteBook(bookToDelete)
      toast({
        title: "Успешно",
        description: "Книга удалена",
      })
      loadBooks()
    } catch (error) {
      toast({
        title: "Ошибка",
        description: "Не удалось удалить книгу",
        variant: "destructive",
      })
    } finally {
      setDeleteDialogOpen(false)
      setBookToDelete(null)
    }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
    setEditingBook(null)
  }

  const handleSuccess = () => {
    loadBooks()
    handleDialogClose()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Управление книгами</h2>
          <p className="text-muted-foreground mt-1">Добавляйте, редактируйте и удаляйте книги из библиотеки</p>
        </div>
        <Button onClick={() => setDialogOpen(true)} className="bg-primary hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Добавить книгу
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
      ) : books.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <BookOpen className="h-16 w-16 text-muted-foreground mb-4" />
            <p className="text-lg font-medium text-foreground">Нет книг</p>
            <p className="text-muted-foreground mb-6">Добавьте первую книгу в библиотеку</p>
            <Button onClick={() => setDialogOpen(true)} className="bg-secondary hover:bg-secondary/90">
              <Plus className="mr-2 h-4 w-4" />
              Добавить книгу
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {books.map((book) => (
            <Card key={book.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg text-balance">{book.title}</CardTitle>
                    <CardDescription className="mt-1">{book.author}</CardDescription>
                  </div>
                  {book.cover_url && (
                    <img
                      src={book.cover_url || "/placeholder.svg"}
                      alt={book.title}
                      className="w-16 h-20 object-cover rounded"
                    />
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-3 mb-4">{book.description}</p>
                {book.tags && book.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {book.tags.map((tag, idx) => (
                      <Badge key={idx} variant="secondary" className="bg-accent text-accent-foreground">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    {book.published_year ? `${book.published_year} г.` : "Год не указан"}
                  </span>
                  <span className="text-muted-foreground">Прочитано: {book.read_count}</span>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm" onClick={() => handleEdit(book)} className="flex-1">
                    <Pencil className="mr-2 h-4 w-4" />
                    Изменить
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => {
                      setBookToDelete(book.id)
                      setDeleteDialogOpen(true)
                    }}
                    className="flex-1"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Удалить
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <BookDialog open={dialogOpen} onOpenChange={handleDialogClose} book={editingBook} onSuccess={handleSuccess} />

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Вы уверены?</AlertDialogTitle>
            <AlertDialogDescription>
              Это действие нельзя отменить. Книга будет удалена безвозвратно.
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
