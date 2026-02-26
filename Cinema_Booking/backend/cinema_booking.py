import uuid
from datetime import datetime


# ─────────────────────────────────────────
# CLASS 1: Movie
# ─────────────────────────────────────────
class Movie:
    """
    Represents a single movie.
    DSA: Dictionary for time_slots → O(1) slot lookup
    """

    def __init__(self, movie_id: int, name: str, genre: str, rating: float, 
                 poster_url: str, slots: list[str], seats_per_slot: int):
        self.movie_id = movie_id
        self.name = name
        self.genre = genre
        self.rating = rating
        self.poster_url = poster_url
        self.total_tickets_sold = 0

        # Dictionary: { "10:00 AM": {"total": 100, "available": 100} }
        self.time_slots: dict[str, dict] = {}
        for slot in slots:
            self.time_slots[slot] = {
                "total": seats_per_slot,
                "available": seats_per_slot
            }

    def display(self):
        print(f"\n  [{self.movie_id}] {self.name}")
        print(f"      Genre: {self.genre} | Rating: ⭐ {self.rating}")
        print(f"      Tickets Sold: {self.total_tickets_sold}")
        for slot, info in self.time_slots.items():
            print(f"      ⏰ {slot} → Available: {info['available']}/{info['total']}")

    def book_seats(self, slot: str, count: int) -> bool:
        """Reduce available seats. O(1) dictionary access."""
        if slot not in self.time_slots:
            return False
        if self.time_slots[slot]["available"] < count:
            return False
        self.time_slots[slot]["available"] -= count
        self.total_tickets_sold += count
        return True

    def restore_seats(self, slot: str, count: int):
        """Restore seats on cancellation. O(1)."""
        if slot in self.time_slots:
            self.time_slots[slot]["available"] += count
            self.total_tickets_sold -= count

    def to_dict(self):
        """Convert movie to dictionary for JSON serialization."""
        return {
            "id": self.movie_id,
            "name": self.name,
            "genre": self.genre,
            "rating": self.rating,
            "poster_url": self.poster_url,
            "slots": self.time_slots,
            "tickets_sold": self.total_tickets_sold
        }


# ─────────────────────────────────────────
# CLASS 2: Ticket
# ─────────────────────────────────────────
class Ticket:
    """
    Stores all booking details for one transaction.
    DSA: Used as value in BookingSystem's HashMap (dict)
    """

    NORMAL = "Normal Customer"
    VIP    = "VIP Member"

    def __init__(self, customer_name: str, booking_type: str,
                 movie_name: str, slot: str, seats: int):
        # UUID ensures uniqueness → O(1) amortized generation
        self.ticket_id    = str(uuid.uuid4())[:8].upper()
        self.customer_name = customer_name
        self.booking_type  = booking_type
        self.movie_name    = movie_name
        self.slot          = slot
        self.seats         = seats
        self.booked_at     = datetime.now().strftime("%Y-%m-%d %H:%M")

    def display(self):
        print(f"""
  
           BOOKING CONFIRMED        
 
      Ticket ID   : {self.ticket_id:<18} 
      Name        : {self.customer_name:<18} 
      Type        : {self.booking_type:<18} 
      Movie       : {self.movie_name:<18} 
      Slot        : {self.slot:<18}
      Seats       : {str(self.seats):<18}
      Booked At   : {self.booked_at:<18} 
                  Enjoy the show! 🎬
        """)

    def __dict__(self):
        """Return ticket as dictionary for JSON response."""
        return {
            "ticket_id": self.ticket_id,
            "customer_name": self.customer_name,
            "booking_type": self.booking_type,
            "movie_name": self.movie_name,
            "slot": self.slot,
            "seats": self.seats,
            "booked_at": self.booked_at
        }


# ─────────────────────────────────────────
# CLASS 3: BookingSystem
# ─────────────────────────────────────────
class BookingSystem:
    """
    Central controller.
    DSA Used:
      - List (Array)   → store movies
      - Dictionary     → store tickets (HashMap, ticket_id → Ticket)
    """

    def __init__(self):
        # List / Array → O(n) search by ID, O(1) append
        self.movies: list[Movie] = []

        # HashMap → O(1) search, insert, delete by ticket_id
        self.tickets: dict[str, Ticket] = {}

        self._preload_movies()

    # ── 1. PRELOAD MOVIES ──────────────────
    def _preload_movies(self):
        """Preload movies: 5 Hollywood + 5 Bollywood with posters."""
        preloaded = [
            # ── HOLLYWOOD MOVIES ──
            Movie(
                1, 
                "Interstellar", 
                "Sci-Fi",
                8.6,
                "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCu6dL8r8f37.jpg",
                ["10:00 AM", "02:00 PM", "07:00 PM"], 
                120
            ),
            Movie(
                2, 
                "Inception", 
                "Thriller",
                8.8,
                "https://image.tmdb.org/t/p/w500/oYuLEwtmpWow0ZVrGnCvMcstna5.jpg",
                ["11:00 AM", "03:00 PM", "08:00 PM"], 
                100
            ),
            Movie(
                3, 
                "The Dark Knight", 
                "Action",
                9.0,
                "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0hl.jpg",
                ["09:00 AM", "01:00 PM", "06:00 PM"], 
                150
            ),
            Movie(
                4, 
                "Dune Part Two", 
                "Sci-Fi",
                8.0,
                "https://image.tmdb.org/t/p/w500/eggspzJRx4WZAcl6eMJustzVMDi.jpg",
                ["12:00 PM", "04:00 PM", "09:00 PM"], 
                80
            ),
            Movie(
                5, 
                "Oppenheimer", 
                "Biography",
                8.5,
                "https://image.tmdb.org/t/p/w500/jQ0aGi2l_cjIvNQQUno2msI6alO.jpg",
                ["10:30 AM", "02:30 PM", "07:30 PM"], 
                110
            ),
            # ── BOLLYWOOD MOVIES ──
            Movie(
                6,
                "Badla",
                "Crime Thriller",
                7.7,
                "https://image.tmdb.org/t/p/w500/lLQV3GR6U9Zz1kxH1I6jM8wHqIx.jpg",
                ["10:00 AM", "02:30 PM", "07:15 PM"],
                140
            ),
            Movie(
                7,
                "Baahubali 2",
                "Action",
                8.2,
                "https://image.tmdb.org/t/p/w500/J8weWC8aZ3gLVSYWD6Fq5iIHfEp.jpg",
                ["11:00 AM", "03:30 PM", "08:30 PM"],
                130
            ),
            Movie(
                8,
                "War",
                "Action",
                6.6,
                "https://image.tmdb.org/t/p/w500/2Fnv0fBzp0bYf3u3bxNHdx0oKrV.jpg",
                ["10:15 AM", "02:45 PM", "07:30 PM"],
                125
            ),
            Movie(
                9,
                "Phir Hera Pheri",
                "Comedy",
                7.4 ,
                "https://image.tmdb.org/t/p/w500/kS5jPEQvhfCRR2xeYc5dZyQnGD8.jpg",
                ["10:30 AM", "03:00 PM", "08:00 PM"],
                115
            ),
            Movie(
                10,
                "PK",
                "Comedy",
                6.8,
                "https://image.tmdb.org/t/p/w500/5k7D2MQSgN8qv5THnvQRQsyDTQS.jpg",
                ["09:30 AM", "01:30 PM", "06:45 PM"],
                120
            ),
        ]
        self.movies.extend(preloaded)
        print(f"✅ {len(self.movies)} movies preloaded into system (5 Hollywood + 5 Bollywood).")

    # ── 2. DISPLAY ALL MOVIES ──────────────
    def display_movies(self):
        """
        O(n * s) where n = movies, s = slots per movie.
        Iterates over the list array.
        """
        print(f"\n{'═'*60}")
        print(f"  🎬 CINEMA BOOKING SYSTEM — {len(self.movies)} Movies")
        print(f"{'═'*60}")
        
        # Display Hollywood movies
        print("\n  🎥 HOLLYWOOD MOVIES")
        print(f"  {'-'*56}")
        for movie in self.movies[:5]:
            movie.display()
        
        # Display Bollywood movies
        print("\n  🎥 BOLLYWOOD MOVIES")
        print(f"  {'-'*56}")
        for movie in self.movies[5:]:
            movie.display()
        
        print(f"{'═'*60}")

    # ── Helper: find movie by ID ───────────
    def _find_movie(self, movie_id: int) -> Movie | None:
        """Linear search O(n). Acceptable for small lists."""
        for movie in self.movies:
            if movie.movie_id == movie_id:
                return movie
        return None

    # ── 3. BOOK TICKET ────────────────────
    def book_ticket(self):
        """
        Collects user input, validates, and books seats.
        DSA: Dict insert O(1), list search O(n)
        """
        self.display_movies()

        try:
            mid = int(input("\nEnter Movie ID: "))
        except ValueError:
            print("❌ Invalid input. Enter a number.")
            return

        movie = self._find_movie(mid)
        if not movie:
            print(f"❌ Movie ID {mid} not found.")
            return

        print(f"\nAvailable slots for '{movie.name}':")
        slots = list(movie.time_slots.keys())
        for i, s in enumerate(slots, 1):
            info = movie.time_slots[s]
            print(f"  {i}. {s}  (Available: {info['available']})")

        try:
            si = int(input("Choose slot number: ")) - 1
            if si < 0 or si >= len(slots):
                raise ValueError
            slot = slots[si]
        except ValueError:
            print("❌ Invalid slot selection.")
            return

        try:
            seats = int(input("Number of seats: "))
            if seats <= 0:
                raise ValueError
        except ValueError:
            print("❌ Enter a positive number of seats.")
            return

        print("Booking Type:\n  1. Normal Customer\n  2. VIP Member")
        btype_input = input("Choose (1/2): ").strip()
        booking_type = Ticket.VIP if btype_input == "2" else Ticket.NORMAL

        name = input("Enter Customer Name: ").strip()
        if not name:
            print("❌ Name cannot be empty.")
            return

        if not movie.book_seats(slot, seats):
            print(f"❌ Not enough seats. Available: {movie.time_slots[slot]['available']}")
            return

        ticket = Ticket(name, booking_type, movie.name, slot, seats)
        self.tickets[ticket.ticket_id] = ticket   # O(1) HashMap insert
        ticket.display()

    # ── 4. CANCEL TICKET ──────────────────
    def cancel_ticket(self):
        """
        O(1) search in HashMap, O(n) to find movie.
        """
        tid = input("Enter Ticket ID to cancel: ").strip().upper()

        if tid not in self.tickets:          # O(1) hash lookup
            print(f"❌ Ticket ID '{tid}' not found.")
            return

        ticket = self.tickets[tid]
        movie  = self._find_movie_by_name(ticket.movie_name)

        if movie:
            movie.restore_seats(ticket.slot, ticket.seats)

        del self.tickets[tid]               # O(1) hash delete
        print(f"✅ Ticket {tid} cancelled. Seats restored for '{ticket.movie_name}' @ {ticket.slot}.")

    def _find_movie_by_name(self, name: str) -> Movie | None:
        """O(n) linear search by name."""
        for movie in self.movies:
            if movie.name == name:
                return movie
        return None

    # ── 5. SEARCH TICKET ──────────────────
    def search_ticket(self):
        """
        O(1) HashMap lookup — the core DSA advantage.
        """
        tid = input("Enter Ticket ID: ").strip().upper()

        ticket = self.tickets.get(tid)      # O(1)
        if not ticket:
            print(f"❌ Ticket '{tid}' not found.")
            return

        print(f"""
  🔍 Ticket Details
  ─────────────────────────────────
  Ticket ID    : {ticket.ticket_id}
  Customer     : {ticket.customer_name}
  Booking Type : {ticket.booking_type}
  Movie        : {ticket.movie_name}
  Time Slot    : {ticket.slot}
  Seats Booked : {ticket.seats}
  Booked At    : {ticket.booked_at}""")

    # ── 6. POPULAR MOVIES ─────────────────
    def show_popular_movies(self):
        """
        Sort movies by total_tickets_sold descending.
        Algorithm: Python's Timsort → O(n log n)
        Alternative shown: Linear max scan O(n)
        """
        if not self.movies:
            print("No movies available.")
            return

        # — Method A: Sorting (O n log n) —
        sorted_movies = sorted(self.movies,
                               key=lambda m: m.total_tickets_sold,
                               reverse=True)

        print(f"\n{'═'*50}")
        print("  🏆 MOVIES BY POPULARITY (Sorted)")
        print(f"{'═'*50}")
        for rank, movie in enumerate(sorted_movies, 1):
            bar = "█" * (movie.total_tickets_sold // 5) if movie.total_tickets_sold else ""
            print(f"  #{rank} {movie.name:<25} ({movie.genre:<10}) {movie.total_tickets_sold:>4} sold {bar}")

        # — Method B: Max scan (O n) —
        max_movie = max(self.movies, key=lambda m: m.total_tickets_sold)
        print(f"\n  🥇 Most Popular: {max_movie.name} ({max_movie.total_tickets_sold} tickets sold)")
        print(f"{'═'*50}")

    # ── 7. VIEW ALL TICKETS ───────────────
    def view_all_tickets(self):
        """Iterate over dict values → O(n)."""
        if not self.tickets:
            print("No tickets booked yet.")
            return
        print(f"\n  📋 All Active Tickets ({len(self.tickets)} total)")
        print("  " + "─"*70)
        for tid, t in self.tickets.items():
            print(f"  {tid} | {t.customer_name:<15} | {t.movie_name:<25} | {t.slot:<12} | {t.seats} seat(s)")


# ─────────────────────────────────────────
# DRIVER CODE — Main Menu
# ─────────────────────────────────────────
def main():
    system = BookingSystem()

    menu = """
     🎬 CINEMA BOOKING SYSTEM         

 1. Display All Movies               
 2. Book a Ticket                    
 3. Cancel a Ticket                  
 4. Search Ticket by ID              
 5. Show Popular Movies              
 6. View All Active Tickets          
 0. Exit                             
"""

    while True:
        print(menu)
        choice = input("Enter choice: ").strip()

        if   choice == "1": system.display_movies()
        elif choice == "2": system.book_ticket()
        elif choice == "3": system.cancel_ticket()
        elif choice == "4": system.search_ticket()
        elif choice == "5": system.show_popular_movies()
        elif choice == "6": system.view_all_tickets()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
