"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BookManagement } from "@/components/book-management"
import { EventManagement } from "@/components/event-management"
import { BookOpen, Calendar } from "lucide-react"

export function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("books")

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-primary">LibraLife</h1>
          <p className="text-muted-foreground mt-1">Панель управления</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="books" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Книги
            </TabsTrigger>
            <TabsTrigger value="events" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Мероприятия
            </TabsTrigger>
          </TabsList>

          <TabsContent value="books" className="mt-0">
            <BookManagement />
          </TabsContent>

          <TabsContent value="events" className="mt-0">
            <EventManagement />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
