from flask import Flask, jsonify, request
from flask_cors import CORS
from cinema_booking import BookingSystem

app = Flask(__name__)
CORS(app)

system = BookingSystem()

# ============================================================================
# GET MOVIES - Returns all movies with poster URLs, genre, and rating
# ============================================================================
@app.route("/movies", methods=["GET"])
def get_movies():
    """
    Returns list of all movies with:
    - id, name, genre, rating, poster_url
    - time_slots with available seats
    - tickets_sold count
    """
    movies = []
    for m in system.movies:
        movie_data = {
            "id": m.movie_id,
            "name": m.name,
            "genre": m.genre,
            "rating": m.rating,
            "poster_url": m.poster_url,
            "slots": m.time_slots,
            "tickets_sold": m.total_tickets_sold
        }
        movies.append(movie_data)
    return jsonify(movies)


# ============================================================================
# BOOK TICKET - Creates a new booking
# ============================================================================
@app.route("/book", methods=["POST"])
def book_ticket():
    """
    Request body:
    {
        "movie_id": 1,
        "slot": "10:00 AM",
        "seats": 2,
        "name": "John Doe",
        "type": "Normal" or "VIP"
    }
    
    Returns ticket_id on success
    """
    data = request.json
    
    # Validate request
    if not all(key in data for key in ["movie_id", "slot", "seats", "name", "type"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        movie_id = int(data["movie_id"])
        seats = int(data["seats"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid movie_id or seats"}), 400
    
    # Find movie
    movie = system._find_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    
    # Validate slot
    if data["slot"] not in movie.time_slots:
        return jsonify({"error": "Invalid slot"}), 400
    
    # Check available seats
    if not movie.book_seats(data["slot"], seats):
        available = movie.time_slots[data["slot"]]["available"]
        return jsonify({
            "error": f"Not enough seats. Available: {available}"
        }), 400
    
    # Create ticket
    from cinema_booking import Ticket
    ticket = Ticket(
        data["name"],
        data["type"],
        movie.name,
        data["slot"],
        seats
    )
    
    system.tickets[ticket.ticket_id] = ticket
    
    return jsonify({
        "message": "Booked successfully",
        "ticket_id": ticket.ticket_id
    }), 201


# ============================================================================
# GET TICKET - Retrieve booking details by ticket ID
# ============================================================================
@app.route("/ticket/<ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    """
    Returns ticket details:
    {
        "ticket_id": "ABC12345",
        "customer_name": "John Doe",
        "booking_type": "Normal Customer",
        "movie_name": "Pathaan",
        "slot": "10:00 AM",
        "seats": 2,
        "booked_at": "2024-02-24 10:30"
    }
    """
    ticket = system.tickets.get(ticket_id.upper())
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    return jsonify({
        "ticket_id": ticket.ticket_id,
        "customer_name": ticket.customer_name,
        "booking_type": ticket.booking_type,
        "movie_name": ticket.movie_name,
        "slot": ticket.slot,
        "seats": ticket.seats,
        "booked_at": ticket.booked_at
    }), 200


# ============================================================================
# CANCEL TICKET - Delete a booking and restore seats
# ============================================================================
@app.route("/cancel/<ticket_id>", methods=["DELETE"])
def cancel_ticket(ticket_id):
    """
    Cancels a ticket and restores seats to the movie
    """
    ticket = system.tickets.get(ticket_id.upper())
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    # Find and update movie
    movie = system._find_movie_by_name(ticket.movie_name)
    if movie:
        movie.restore_seats(ticket.slot, ticket.seats)
    
    # Delete ticket
    del system.tickets[ticket_id.upper()]
    
    return jsonify({
        "message": "Ticket cancelled successfully",
        "ticket_id": ticket_id.upper()
    }), 200


# ============================================================================
# GET POPULAR MOVIES - Returns movies sorted by tickets sold
# ============================================================================
@app.route("/popular", methods=["GET"])
def get_popular_movies():
    """
    Returns movies sorted by tickets_sold in descending order
    """
    movies = []
    sorted_movies = sorted(
        system.movies,
        key=lambda m: m.total_tickets_sold,
        reverse=True
    )
    
    for m in sorted_movies:
        movie_data = {
            "id": m.movie_id,
            "name": m.name,
            "genre": m.genre,
            "rating": m.rating,
            "poster_url": m.poster_url,
            "tickets_sold": m.total_tickets_sold
        }
        movies.append(movie_data)
    
    return jsonify(movies), 200


# ============================================================================
# GET MOVIE BY ID - Get specific movie details
# ============================================================================
@app.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie_by_id(movie_id):
    """
    Returns details of a specific movie
    """
    movie = system._find_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    
    movie_data = {
        "id": movie.movie_id,
        "name": movie.name,
        "genre": movie.genre,
        "rating": movie.rating,
        "poster_url": movie.poster_url,
        "slots": movie.time_slots,
        "tickets_sold": movie.total_tickets_sold
    }
    
    return jsonify(movie_data), 200


# ============================================================================
# GET AVAILABLE SLOTS - Get available seats for a movie/slot
# ============================================================================
@app.route("/slots/<int:movie_id>", methods=["GET"])
def get_available_slots(movie_id):
    """
    Returns available seats for all slots of a movie
    """
    movie = system._find_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    
    slots_data = {}
    for slot, info in movie.time_slots.items():
        slots_data[slot] = {
            "total": info["total"],
            "available": info["available"],
            "booked": info["total"] - info["available"]
        }
    
    return jsonify({
        "movie_id": movie.movie_id,
        "movie_name": movie.name,
        "slots": slots_data
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "movies_count": len(system.movies),
        "tickets_count": len(system.tickets)
    }), 200


# ============================================================================
# ROOT ENDPOINT - API Documentation
# ============================================================================
@app.route("/", methods=["GET"])
def api_docs():
    """
    API Documentation
    """
    return jsonify({
        "app": "Cinema Booking System API",
        "version": "2.0",
        "endpoints": {
            "GET /movies": "Get all movies with posters and ratings",
            "GET /movie/<id>": "Get specific movie details",
            "GET /popular": "Get movies sorted by popularity",
            "GET /slots/<id>": "Get available slots for a movie",
            "POST /book": "Book a ticket",
            "GET /ticket/<id>": "Get ticket details",
            "DELETE /cancel/<id>": "Cancel a ticket",
            "GET /health": "Health check"
        },
        "movies": {
            "hollywood": ["Interstellar", "Inception", "The Dark Knight", "Dune Part Two", "Oppenheimer"],
            "bollywood": ["Pathaan", "Jawan", "Fighter", "Teri Baaton Mein Aisa Uljha Jiya", "Bhaiyya Ji"]
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
