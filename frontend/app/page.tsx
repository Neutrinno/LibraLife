import Header from "@/components/header"
import Hero from "@/components/hero"
import Knowledge from "@/components/knowledge"
import NewBooks from "@/components/new-books"
import Events from "@/components/events"
import Footer from "@/components/footer"

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <Hero />
      <Knowledge />
      <NewBooks />
      <Events />
      <Footer />
    </div>
  )
}
