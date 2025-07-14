// Fetch book data from API
async function fetchBookData(bookId) {
    try {
        const response = await fetch(`/api/books/${bookId}`);
        if (!response.ok) throw new Error('Book not found');
        return await response.json();
    } catch (error) {
        console.error('Error fetching book data:', error);
        return null;
    }
}

// Fetch related books from API by category name
async function fetchRelatedBooks(categoryName, excludeBookId) {
    try {
        // First, get all books in the same category
        const params = new URLSearchParams({ limit: 8 });
        const response = await fetch(`/api/books?search=${encodeURIComponent(categoryName)}`);
        if (!response.ok) throw new Error('Failed to fetch related books');
        let books = await response.json();
        // Exclude the current book
        books = books.filter(b => b.id !== excludeBookId);
        return books;
    } catch (error) {
        console.error('Error fetching related books:', error);
        return [];
    }
}

// Function to get book ID from URL
function getBookIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    const id = pathParts[pathParts.length - 1];
    return isNaN(Number(id)) ? null : id;
}

// Function to render star rating
function renderStarRating(rating) {
    const starContainer = document.getElementById('starRating');
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    starContainer.innerHTML = '';

    // Full stars
    for (let i = 0; i < fullStars; i++) {
        starContainer.innerHTML += '<i class="fas fa-star"></i>';
    }

    // Half star
    if (hasHalfStar) {
        starContainer.innerHTML += '<i class="fas fa-star-half-alt"></i>';
    }

    // Empty stars
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        starContainer.innerHTML += '<i class="far fa-star"></i>';
    }
}

// Function to update availability status
function updateAvailabilityStatus(book) {
    const badge = document.getElementById('availabilityBadge');
    const borrowBtn = document.getElementById('borrowBtn');
    const onlineBtn = document.getElementById('onlineBtn');

    if (book.storage_type === 'online') {
        badge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 availability-badge mb-6';
        badge.innerHTML = '<i class="fas fa-circle text-blue-400 mr-2 text-xs"></i>Available Online';

        if (book.access_url) {
            onlineBtn.style.display = 'block';
            onlineBtn.onclick = () => window.open(book.access_url, '_blank');
        }
    } else if (book.quantity > 0) {
        badge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 availability-badge mb-6';
        badge.innerHTML = '<i class="fas fa-circle text-green-400 mr-2 text-xs"></i>Available (' + book.quantity + ' copies)';
    } else {
        badge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 availability-badge mb-6';
        badge.innerHTML = '<i class="fas fa-circle text-red-400 mr-2 text-xs"></i>Not Available';
        borrowBtn.disabled = true;
        borrowBtn.className = 'w-full bg-gray-400 text-white py-3 px-6 rounded-lg font-semibold cursor-not-allowed';
        borrowBtn.innerHTML = '<i class="fas fa-times mr-2"></i>Not Available';
    }
}

// Function to render book details
function renderBookDetails(book) {
    document.getElementById('bookTitle').textContent = book.title;
    document.getElementById('bookAuthor').innerHTML = `by <span class="font-semibold">${book.author}</span>`;
    document.getElementById('bookCategory').textContent = book.category;
    document.getElementById('bookYear').textContent = book.published_year;
    document.getElementById('bookLanguage').textContent = book.language;
    document.getElementById('bookISBN').textContent = book.isbn;
    document.getElementById('bookPublisher').textContent = book.publisher;
    document.getElementById('storageType').textContent = book.storage_type.charAt(0).toUpperCase() + book.storage_type.slice(1);
    document.getElementById('bookCover').src = book.cover_image;
    document.getElementById('categoryName').textContent = book.category;

    // Update rating
    if (book.rating) {
        renderStarRating(book.rating);
        document.getElementById('ratingValue').textContent = `(${book.rating})`;
    } else {
        document.getElementById('ratingValue').textContent = '(No rating)';
    }

    // Update availability
    updateAvailabilityStatus(book);

    // Update page title
    document.title = `${book.title} - Library Management`;
}

// Function to render related books
function renderRelatedBooks(books) {
    const container = document.getElementById('relatedBooks');
    container.innerHTML = books.map(book => `
                <div class="book-card bg-white rounded-lg shadow-sm overflow-hidden transition-all duration-300 cursor-pointer hover:shadow-lg">
                    <img src="${book.cover_image}" alt="${book.title}" class="w-full h-48 object-cover">
                    <div class="p-4">
                        <h3 class="font-semibold text-gray-900 text-sm mb-1 line-clamp-2">${book.title}</h3>
                        <p class="text-gray-600 text-xs">${book.author}</p>
                    </div>
                </div>
            `).join('');

    // Add click handlers
    container.querySelectorAll('.book-card').forEach((card, index) => {
        card.onclick = () => {
            window.location.href = `/book/${books[index].id}`;
        };
    });
}

// Modal logic for borrow request
function setupBorrowModal() {
    const borrowBtn = document.getElementById('borrowBtn');
    const borrowModal = document.getElementById('borrow-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const borrowForm = document.getElementById('borrow-form');
    const modalBookId = document.getElementById('modal-book-id');
    const requestDescription = document.getElementById('request_description');
    const returnDate = document.getElementById('return_date');

    if (!borrowBtn || !borrowModal || !closeModalBtn || !borrowForm) return;

    // Open modal on borrow button click
    borrowBtn.onclick = function () {
        const bookId = getBookIdFromUrl();
        modalBookId.value = bookId;
        requestDescription.value = '';
        returnDate.value = '';
        borrowModal.classList.remove('hidden');
    };

    // Close modal
    closeModalBtn.onclick = function () {
        borrowModal.classList.add('hidden');
    };

    // Handle form submission
    borrowForm.onsubmit = async function (e) {
        e.preventDefault();
        const bookId = modalBookId.value;
        const desc = requestDescription.value.trim();
        const date = returnDate.value;
        if (!desc || !date) {
            alert('Please fill in all fields.');
            return;
        }
        // Show loading state
        const submitBtn = borrowForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Submitting...';
        submitBtn.disabled = true;
        try {
            const res = await fetch('/api/borrow/request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    book_id: bookId,
                    request_description: desc,
                    return_date: date
                })
            });
            const data = await res.json();
            if (data.success) {
                alert('Borrow request sent!');
                borrowModal.classList.add('hidden');
            } else {
                alert('Failed to request: ' + (data.error || 'Unknown error'));
            }
        } catch (err) {
            alert('Error sending request.');
        }
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    };
}

function hideBookSpinner() {
    const spinner = document.getElementById('book-loading-spinner');
    if (spinner) spinner.style.display = 'none';
}


// Helper: get user's borrow request for this book
async function getMyBorrowRequestForBook(bookId, bookIsbn) {
    try {
        const res = await fetch('/api/mybooks');
        if (!res.ok) return null;
        const myBooks = await res.json();
        return myBooks.find(b => String(b.id || b.book_id) === String(bookId) || b.isbn === bookIsbn) || null;
    } catch (e) {
        return null;
    }
}

// Initialize page
async function initializePage() {
    const bookId = getBookIdFromUrl();
    if (!bookId) {
        document.getElementById('bookTitle').textContent = 'Book Not Found';
        if (window.hideBookSpinner) window.hideBookSpinner();
        return;
    }
    try {
        const book = await fetchBookData(bookId);
        if (book) {
            renderBookDetails(book);
            const bookIsbnForRequestCheck = book.isbn;
            const borrowBtn = document.getElementById('borrowBtn');
            const onlineBtn = document.getElementById('onlineBtn');
            let offlineAddressDiv = document.getElementById('offlineAddress');
            if (!offlineAddressDiv) {
                // Create offline address div if not present
                offlineAddressDiv = document.createElement('div');
                offlineAddressDiv.id = 'offlineAddress';
                offlineAddressDiv.style.display = 'none';
                offlineAddressDiv.className = 'mt-4 text-sm text-gray-700';
                // Insert after action buttons
                const actionBtns = borrowBtn ? borrowBtn.parentElement : null;
                if (actionBtns) actionBtns.appendChild(offlineAddressDiv);
            }

            const myRequest = await getMyBorrowRequestForBook(bookId, bookIsbnForRequestCheck);
            if (myRequest && myRequest.status === 'approved') {
                // Hide borrow button
                if (borrowBtn) borrowBtn.style.display = 'none';
                // Show online access if online
                if (book.storage_type === 'online' && onlineBtn) {
                    onlineBtn.style.display = '';
                    onlineBtn.onclick = () => window.open(book.access_url || book.online_address || '#', '_blank');
                } else if (book.storage_type === 'offline') {
                    // Show offline address/location from API
                    if (offlineAddressDiv) {
                        try {
                            const response = await fetch(`/api/books/${bookId}/offline_address`);

                            if (response.ok) {
                                const data = await response.json();

                                let html = `
  <ul class="pl-5 space-y-2 list-none bg-white shadow-md rounded-md p-4 border border-gray-200">
    ${data.address ? `<li class="flex items-start"><span class="font-semibold text-blue-600 w-24">Location</span><span class="text-gray-700">${data.address}</span></li>` : ''}
    ${data.shelf_no ? `<li class="flex items-start"><span class="font-semibold text-blue-600 w-24">Shelf</span><span class="text-gray-700">${data.shelf_no}</span></li>` : ''}
    ${data.room ? `<li class="flex items-start"><span class="font-semibold text-blue-600 w-24">Room</span><span class="text-gray-700">${data.room}</span></li>` : ''}
  </ul>
`;


                                // If no fields exist, show fallback message
                                if (!data.address && !data.shelf_no && !data.room) {
                                    offlineAddressDiv.textContent = 'Location: Ask librarian';
                                } else {
                                    offlineAddressDiv.innerHTML = html;
                                }

                            } else {
                                offlineAddressDiv.textContent = 'Location: Ask librarian';
                            }
                        } catch (error) {
                            offlineAddressDiv.textContent = 'Location: Ask librarian';
                        }

                        offlineAddressDiv.classList.remove('hidden');
                    }

                    if (onlineBtn) {
                        onlineBtn.style.display = 'none';
                    }

                }
            } else {
                // Not approved: hide online access and offline address
                if (onlineBtn) onlineBtn.style.display = 'none';
                if (offlineAddressDiv) offlineAddressDiv.style.display = 'none';
                // Show/hide borrow button as before
                if (borrowBtn) {
                    const alreadyRequested = !!myRequest;
                    borrowBtn.style.display = alreadyRequested ? 'none' : '';
                }
            }
            // Fetch related books by category
            const relatedBooks = await fetchRelatedBooks(book.category, book.id);
            renderRelatedBooks(relatedBooks);
        } else {
            document.getElementById('bookTitle').textContent = 'Book Not Found';
        }
    } catch (error) {
        console.error('Error initializing page:', error);
    }
    if (window.hideBookSpinner) window.hideBookSpinner();
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initializePage();
    setupBorrowModal();
});