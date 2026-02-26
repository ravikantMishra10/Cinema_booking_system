// ============================================================================
// CINEMA BOOKING APP - REFACTORED SCRIPT
// ============================================================================

const API = "http://127.0.0.1:5000";

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
  movies: [],
  selectedMovie: null,
  selectedSlot: null,
  selectedSeats: 1,
  isLoading: false,
  pricePerSeat: 500, // Default price in INR
  currencySymbol: '₹', // Indian Rupees
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initializeApp();
});

function initializeApp() {
  fetchMovies();
  loadLastBooking();
  setupEventListeners();
}

function setupEventListeners() {
  // Close modal when pressing Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeBookingModal();
      closeConfirmation();
    }
  });

  // Update price when seat quantity changes
  document.getElementById('seatInput').addEventListener('change', updatePriceSummary);

  // Search ticket on Enter key
  document.getElementById('search_id').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchTicket();
  });
}

// ============================================================================
// MOVIES MANAGEMENT
// ============================================================================

function fetchMovies() {
  showLoadingSpinner(true);
  
  fetch(`${API}/movies`)
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch movies');
      return res.json();
    })
    .then(data => {
      state.movies = data;
      renderMovies();
      showLoadingSpinner(false);
    })
    .catch(error => {
      console.error('Error fetching movies:', error);
      showToast('Failed to load movies. Please refresh the page.', 'error');
      showLoadingSpinner(false);
    });
}

function renderMovies() {
  const container = document.getElementById('movieGrid');
  const emptyState = document.getElementById('emptyState');
  
  container.innerHTML = '';

  if (!state.movies || state.movies.length === 0) {
    emptyState.classList.remove('hidden');
    return;
  }

  emptyState.classList.add('hidden');

  state.movies.forEach(movie => {
    const card = createMovieCard(movie);
    container.appendChild(card);
  });
}

function createMovieCard(movie) {
  const card = document.createElement('div');
  card.className = 'movie-card';
  
  const hasSlots = movie.slots && Object.keys(movie.slots).length > 0;
  
  // Use poster_url from backend, fallback to placeholder
  const posterUrl = movie.poster_url || `https://via.placeholder.com/300x450?text=${encodeURIComponent(movie.name)}`;
  
  card.innerHTML = `
    <div class="movie-poster-container">
      <img src="${posterUrl}" 
           alt="${movie.name}"
           loading="lazy"
           class="movie-poster"
           onerror="this.src='https://via.placeholder.com/300x450?text=${encodeURIComponent(movie.name)}'">
      <div class="movie-overlay"></div>
    </div>
    <div class="movie-info">
      <h3>${escapeHtml(movie.name)}</h3>
      ${movie.genre ? `<p class="movie-genre">${escapeHtml(movie.genre)}</p>` : ''}
      ${movie.rating ? `<p class="movie-rating">⭐ ${movie.rating}</p>` : ''}
      <button class="btn btn-primary btn-sm" 
              onclick="openBookingModal(${movie.id})"
              ${!hasSlots ? 'disabled' : ''}>
        ${hasSlots ? 'Book Now' : 'No Shows'}
      </button>
    </div>
  `;
  
  return card;
}

// ============================================================================
// BOOKING MODAL
// ============================================================================

function openBookingModal(movieId) {
  state.selectedMovie = state.movies.find(m => m.id === movieId);
  state.selectedSlot = null;
  state.selectedSeats = 1;

  if (!state.selectedMovie) {
    showToast('Movie not found', 'error');
    return;
  }

  // Set modal title
  document.getElementById('modalMovieTitle').innerText = state.selectedMovie.name;

  // Render slot buttons
  renderSlotButtons();

  // Reset form inputs
  document.getElementById('seatInput').value = '1';
  document.getElementById('nameInput').value = '';
  document.getElementById('typeInput').value = 'Normal';
  document.getElementById('confirmBookingBtn').disabled = true;

  // Update price summary
  updatePriceSummary();

  // Show modal
  document.getElementById('bookingModal').classList.remove('hidden');
  document.body.style.overflow = 'hidden'; // Prevent background scroll
}

function closeBookingModal(event) {
  // Close only if clicking overlay or close button
  if (event && event.target.id !== 'bookingModal') return;

  document.getElementById('bookingModal').classList.add('hidden');
  document.body.style.overflow = '';
  
  // Reset state
  state.selectedSlot = null;
}

function renderSlotButtons() {
  const container = document.getElementById('modalSlots');
  container.innerHTML = '';

  if (!state.selectedMovie.slots || Object.keys(state.selectedMovie.slots).length === 0) {
    container.innerHTML = '<p style="grid-column: 1/-1; color: #cbd5e1;">No available slots</p>';
    return;
  }

  Object.keys(state.selectedMovie.slots).forEach(slot => {
    const btn = document.createElement('button');
    btn.className = 'slot-buttons-btn';
    btn.textContent = slot;
    btn.onclick = (e) => {
      e.preventDefault();
      selectSlot(slot, btn);
    };
    
    container.appendChild(btn);
  });
}

function selectSlot(slot, buttonElement) {
  state.selectedSlot = slot;

  // Update button styles
  document.querySelectorAll('.slot-buttons button').forEach(btn => {
    btn.classList.remove('selected');
  });
  buttonElement.classList.add('selected');

  // Enable confirm button
  updateConfirmButtonState();
}

function changeSeat(delta) {
  const input = document.getElementById('seatInput');
  let current = parseInt(input.value) || 1;
  const newValue = Math.max(1, Math.min(10, current + delta));
  
  input.value = newValue;
  state.selectedSeats = newValue;
  updatePriceSummary();
  updateConfirmButtonState();
}

function updatePriceSummary() {
  const seats = parseInt(document.getElementById('seatInput').value) || 1;
  const type = document.getElementById('typeInput').value;
  
  state.selectedSeats = seats;
  
  // VIP pricing: 1.5x the normal price
  const multiplier = type === 'VIP' ? 1.5 : 1;
  const pricePerSeat = state.pricePerSeat * multiplier;
  const total = pricePerSeat * seats;

  document.getElementById('pricePerSeat').textContent = `${state.currencySymbol}${pricePerSeat.toFixed(0)}`;
  document.getElementById('priceQuantity').textContent = seats;
  document.getElementById('priceTotal').textContent = `${state.currencySymbol}${total.toFixed(0)}`;
}

function updateConfirmButtonState() {
  const name = document.getElementById('nameInput').value.trim();
  const hasSlot = state.selectedSlot !== null;
  const hasSeats = state.selectedSeats >= 1;
  
  const btn = document.getElementById('confirmBookingBtn');
  btn.disabled = !name || !hasSlot || !hasSeats;
}

// Enable/disable button as user types name
document.addEventListener('input', (e) => {
  if (e.target.id === 'nameInput' || e.target.id === 'typeInput') {
    updateConfirmButtonState();
  }
});

// ============================================================================
// BOOKING CONFIRMATION
// ============================================================================

function confirmBooking() {
  const seats = document.getElementById('seatInput').value;
  const name = document.getElementById('nameInput').value.trim();
  const type = document.getElementById('typeInput').value;

  // Validation
  if (!name || !state.selectedSlot || !seats) {
    showToast('Please fill in all fields', 'error');
    return;
  }

  // Show loading state
  const btn = document.getElementById('confirmBookingBtn');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.querySelector('.btn-text').classList.add('hidden');
  btn.querySelector('.btn-loader').classList.remove('hidden');

  // Make API request
  fetch(`${API}/book`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      movie_id: state.selectedMovie.id,
      slot: state.selectedSlot,
      seats: parseInt(seats),
      name: name,
      type: type
    })
  })
    .then(res => {
      if (!res.ok) throw new Error('Booking failed');
      return res.json();
    })
    .then(data => {
      if (data.error) {
        throw new Error(data.error);
      }

      // Save ticket ID to localStorage
      localStorage.setItem('lastTicket', data.ticket_id);

      // Show confirmation panel
      showConfirmation(data, seats, type);

      // Close booking modal
      closeBookingModal();

      // Refresh movies list
      fetchMovies();
    })
    .catch(error => {
      console.error('Booking error:', error);
      showToast(error.message || 'Booking failed. Please try again.', 'error');
    })
    .finally(() => {
      // Reset button state
      btn.disabled = false;
      btn.querySelector('.btn-text').classList.remove('hidden');
      btn.querySelector('.btn-loader').classList.add('hidden');
    });
}

function showConfirmation(data, seats, type) {
  const details = document.getElementById('confirmationDetails');
  
  details.innerHTML = `
    <p>
      <strong>Ticket ID:</strong>
      <span id="ticketIdDisplay">${data.ticket_id}</span>
    </p>
    <p>
      <strong>Movie:</strong>
      <span>${escapeHtml(state.selectedMovie.name)}</span>
    </p>
    <p>
      <strong>Showtime:</strong>
      <span>${escapeHtml(state.selectedSlot)}</span>
    </p>
    <p>
      <strong>Seats:</strong>
      <span>${seats}</span>
    </p>
    <p>
      <strong>Type:</strong>
      <span>${type}</span>
    </p>
  `;

  document.getElementById('confirmationPanel').classList.remove('hidden');
  document.body.style.overflow = 'hidden';

  // Show success toast
  showToast('Booking confirmed! Your ticket has been saved.', 'success');
}

function closeConfirmation() {
  document.getElementById('confirmationPanel').classList.add('hidden');
  document.body.style.overflow = '';
  document.getElementById('myBooking').scrollIntoView({ behavior: 'smooth' });
  loadLastBooking();
}

function copyTicketId() {
  const ticketIdElement = document.getElementById('ticketIdDisplay');
  if (!ticketIdElement) return;

  const ticketId = ticketIdElement.textContent;
  
  navigator.clipboard.writeText(ticketId)
    .then(() => {
      showToast('Ticket ID copied to clipboard!', 'success');
    })
    .catch(() => {
      showToast('Failed to copy ticket ID', 'error');
    });
}

// ============================================================================
// MY BOOKINGS
// ============================================================================

function searchTicket() {
  const id = document.getElementById('search_id').value.trim();

  if (!id) {
    showToast('Please enter a Ticket ID', 'error');
    return;
  }

  displayTicket(id, false);
}

function loadLastBooking() {
  const id = localStorage.getItem('lastTicket');
  
  if (id) {
    displayTicket(id, true);
  } else {
    // Show empty state for last booking
    document.getElementById('lastBooking').classList.add('hidden');
    document.getElementById('noLastBooking').classList.remove('hidden');
  }
}

function displayTicket(id, isLast = false) {
  const container = isLast ? 'lastBooking' : 'bookingCard';
  const cardElement = document.getElementById(container);

  fetch(`${API}/ticket/${id}`)
    .then(res => {
      if (!res.ok) throw new Error('Ticket not found');
      return res.json();
    })
    .then(data => {
      if (data.error) {
        throw new Error(data.error);
      }

      renderBookingCard(cardElement, data, isLast);
      
      // Hide empty state if showing last booking
      if (isLast) {
        document.getElementById('noLastBooking').classList.add('hidden');
      }
    })
    .catch(error => {
      console.error('Error fetching ticket:', error);
      
      if (!isLast) {
        showToast('Ticket not found. Please check the ID.', 'error');
        cardElement.classList.add('hidden');
      }
    });
}

function renderBookingCard(cardElement, data, isLast) {
  const innerDiv = cardElement.querySelector('.booking-card-inner') || document.createElement('div');
  innerDiv.className = 'booking-card-inner';

  innerDiv.innerHTML = `
    <h3>${escapeHtml(data.movie_name)}</h3>
    <p>
      <strong>Ticket ID:</strong>
      <span>${data.ticket_id}</span>
    </p>
    <p>
      <strong>Seats:</strong>
      <span>${data.seats}</span>
    </p>
    <p>
      <strong>Showtime:</strong>
      <span>${escapeHtml(data.slot)}</span>
    </p>
    <p>
      <strong>Type:</strong>
      <span>${data.booking_type}</span>
    </p>
    <button class="btn btn-danger btn-sm" onclick="cancelTicket('${data.ticket_id}')">
      Cancel Ticket
    </button>
  `;

  // Only add inner div if it doesn't exist
  if (!cardElement.querySelector('.booking-card-inner')) {
    cardElement.appendChild(innerDiv);
  }

  cardElement.classList.remove('hidden');
}

function cancelTicket(ticketId) {
  if (!confirm('Are you sure you want to cancel this ticket? This action cannot be undone.')) {
    return;
  }

  const btn = event.target;
  btn.disabled = true;
  const originalText = btn.textContent;
  btn.textContent = 'Cancelling...';

  fetch(`${API}/cancel/${ticketId}`, { method: 'DELETE' })
    .then(res => {
      if (!res.ok) throw new Error('Cancellation failed');
      return res.json();
    })
    .then(data => {
      showToast(data.message || 'Ticket cancelled successfully', 'success');
      
      // Refresh movies
      fetchMovies();

      // Clear last ticket if it was cancelled
      if (localStorage.getItem('lastTicket') === ticketId) {
        localStorage.removeItem('lastTicket');
      }

      // Reload booking sections
      document.getElementById('bookingCard').classList.add('hidden');
      document.getElementById('search_id').value = '';
      loadLastBooking();
    })
    .catch(error => {
      console.error('Cancellation error:', error);
      showToast(error.message || 'Failed to cancel ticket', 'error');
      btn.disabled = false;
      btn.textContent = originalText;
    });
}

// ============================================================================
// UI HELPERS
// ============================================================================

function showLoadingSpinner(show) {
  const spinner = document.getElementById('loadingSpinner');
  if (show) {
    spinner.classList.remove('hidden');
  } else {
    spinner.classList.add('hidden');
  }
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  
  container.appendChild(toast);

  // Auto-remove after 4 seconds
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ============================================================================
// UTILITY
// ============================================================================

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }
`;
document.head.appendChild(style);
