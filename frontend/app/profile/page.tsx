import Header from "@/components/header"
import Footer from "@/components/footer"
import BracketFrame from "@/components/bracket-frame"

export default function ProfilePage() {
  // Mock user data
  const user = {
    ticketNumber: "83571034",
    name: "Егор Плотников",
    email: "pitnkve@gmail.com",
    books: [
      {
        id: 1,
        title: "Легенды гор и морей. Монстры и предания Древнего Китая",
        author: "Электра Яншина",
        cover: "/abstract-book-cover.png",
        dateTaken: "11.11",
        dateReturn: "25.11",
      },
    ],
  }

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Header />
      <main className="flex-1 w-full">
        <div className="max-w-6xl mx-auto px-4 py-16 md:py-24">
          {/* Page Title */}
          <div className="mb-16">
            <h1
              className="text-4xl md:text-5xl font-bold text-black"
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              <span className="text-blue-500">⦗</span> ЧИТАТЕЛЬСКИЙ БИЛЕТ <span className="text-blue-500">⦘</span>
            </h1>
          </div>

          {/* Ticket Info Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            {/* Left: Ticket Number and User Info */}
            <BracketFrame color="orange">
              <div className="space-y-3">
                <div className="text-2xl font-bold text-black" style={{ fontFamily: "var(--font-display-family)" }}>
                  № {user.ticketNumber}
                </div>
                <div className="space-y-2">
                  <div className="text-gray-900 font-medium">{user.name}</div>
                  <div className="text-gray-600 text-sm">{user.email}</div>
                </div>
              </div>
            </BracketFrame>

            {/* Right: QR Code */}
            <BracketFrame color="orange">
              <div className="flex items-center justify-center bg-gray-100 rounded p-8">
                <div className="w-32 h-32 bg-black flex items-center justify-center rounded">
                  <div className="text-white text-center text-xs">QR Code</div>
                </div>
              </div>
            </BracketFrame>
          </div>

          {/* Books on Hands Section */}
          <div className="mb-12">
            <h2
              className="text-3xl md:text-4xl font-bold text-black mb-8"
              style={{ fontFamily: "var(--font-display-family)" }}
            >
              <span className="text-blue-500">⦗</span> КНИГИ НА РУКАХ <span className="text-blue-500">⦘</span>
            </h2>
          </div>

          {/* Books List */}
          <div className="space-y-6">
            {user.books.map((book) => (
              <BracketFrame key={book.id} color="orange">
                <div className="flex gap-6">
                  {/* Book Cover */}
                  <div className="flex-shrink-0">
                    <div className="w-24 h-32 bg-gray-200 rounded overflow-hidden">
                      <img
                        src={book.cover || "/placeholder.svg"}
                        alt={book.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>

                  {/* Book Info */}
                  <div className="flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-black mb-2">{book.title}</h3>
                      <p className="text-gray-600 text-sm mb-4">{book.author}</p>
                    </div>

                    {/* Dates */}
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-700 font-medium">Взяли на руки</span>
                        <span className="border-2 border-blue-500 text-blue-500 px-2 py-1 text-sm font-bold rounded">
                          {book.dateTaken}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-700 font-medium">Необходимо вернуть до</span>
                        <span className="border-2 border-blue-500 text-blue-500 px-2 py-1 text-sm font-bold rounded">
                          {book.dateReturn}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </BracketFrame>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
