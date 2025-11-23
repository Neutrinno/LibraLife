import Header from "@/components/header"
import Footer from "@/components/footer"
import EventsList from "@/components/events-list"

export default function EventsPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Header />
      <main className="flex-1 w-full">
        <div className="max-w-6xl mx-auto px-4 py-16 md:py-24">
          {/* Title section */}
          <div className="mb-12">
            <h1
              className="text-4xl md:text-5xl font-bold text-black mb-4"
              style={{ fontFamily: "var(--font-wix-display)" }}
            >
              <span className="text-orange-500">⦗</span> МЕРОПРИЯТИЯ <span className="text-orange-500">⦘</span>
            </h1>
          </div>

          {/* Events list */}
          <EventsList />
        </div>
      </main>
      <Footer />
    </div>
  )
}
