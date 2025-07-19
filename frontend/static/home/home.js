let books = [];

// Fetch dashboard stats and update DOM
async function fetchDashboardStats() {
    try {
        const res = await fetch('/api/dashboard/stats');
        if (!res.ok) throw new Error('Failed to fetch dashboard stats');
        const stats = await res.json();
        document.querySelector('.stat-book').textContent = stats.total_books;
        document.querySelector('.stat-reading').textContent = stats.active_borrowers;
        document.querySelector('.stat-lent').textContent = stats.total_categories;
        document.querySelector('.stat-new').textContent = stats.total_books_last_month;
    } catch (e) {
        console.error('Dashboard stats error:', e);
    }
}

// Fetch all books and update global books array
async function fetchBooks() {
    try {
        const res = await fetch('/api/books');
        if (!res.ok) throw new Error('Failed to fetch books');
        books = await res.json();
        console.log('Fetched books:', books);
        populateBooks();
    } catch (e) {
        console.error('Books fetch error:', e);
    } 
}

// Generate star rating
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 !== 0;
    let stars = "";

    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star text-yellow-400 text-xs"></i>';
    }

    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt text-yellow-400 text-xs"></i>';
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star text-gray-300 text-xs"></i>';
    }

    return stars;
}

function genreToColor(genre) {
    let hash = 0;
    for (let i = 0; i < genre.length; i++) {
        hash = genre.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Convert hash to HSL color
    const hue = Math.abs(hash) % 360; // Keep it in 0–359
    return `hsl(${hue}, 60%, 70%)`; // Light, pastel-like color
}

// Create book card
function createBookCard(book) {
    const truncatedTitle = book.title.length > 10 ? book.title.slice(0, 10) + "..." : book.title;
    const truncatedAuthor = book.author.length > 12 ? book.author.slice(0, 12) + "..." : book.author;
    const truncatedCategory = book.category && book.category.length > 10 ? book.category.slice(0, 10) + "..." : (book.category || "");
    if (book.cover_image) {
        return `
        <div class="book-card p-4 transition-all" data-book-id="${book.id}" style="cursor:pointer;">
            <div class="book-cover bg-gray-100 rounded-lg h-48 mb-4 flex items-center justify-center relative overflow-hidden">
                <img src="${book.cover_image}" alt="${book.title}" class="object-cover w-full h-full rounded-lg" />
            </div>
            <div class="space-y-2">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-semibold text-gray-800 text-sm" title="${book.title}">${truncatedTitle}</h4>
                        <p class="text-gray-600 text-xs">${truncatedAuthor}</p>
                    </div>
                    <div class="flex flex-col items-end">
                        <span class="text-xs font-medium text-gray-700">${book.rating !== undefined ? book.rating.toFixed(1) : 'N/A'}</span>
                        <span>${book.rating !== undefined ? generateStars(book.rating) : ''}</span>
                    </div>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs" style="color: ${genreToColor(book.category || "General")}" title="${book.category || "General"}">${truncatedCategory}</span>
                    <span class="text-xs text-gray-500">${book.published_year || ""}</span>
                </div>
            </div>
        </div>
        `;
    } else {
        return `
        <div class="book-card p-4 transition-all" data-book-id="${book.id}" style="cursor:pointer;">
            <div class="book-cover bg-gray-100 rounded-lg h-48 mb-4 flex items-center justify-center relative overflow-hidden">
                <div class="absolute inset-0 bg-black/10"></div>
                <div class="text-white text-center z-10">
                    <h3 class="font-bold text-lg mb-1" title="${book.title}">${truncatedTitle}</h3>
                    <p class="text-sm opacity-90">${truncatedAuthor}</p>
                </div>
            </div>
            <div class="space-y-2">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-semibold text-gray-800 text-sm" title="${book.title}">${truncatedTitle}</h4>
                        <p class="text-gray-600 text-xs">${truncatedAuthor}</p>
                    </div>
                    <div class="flex flex-col items-end">
                        <span class="text-xs font-medium text-gray-700">${book.rating !== undefined ? book.rating.toFixed(1) : 'N/A'}</span>
                        <span>${book.rating !== undefined ? generateStars(book.rating) : ''}</span>
                    </div>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs" style="color: ${genreToColor(book.category || "General")}" title="${book.category || "General"}">${truncatedCategory}</span>
                    <span class="text-xs text-gray-500">${book.published_year || ""}</span>
                </div>
            </div>
        </div>
        `;
    }
}

// Populate books
function populateBooks() {
    const recentlyAddedContainer = document.getElementById("recentlyAdded");
    const allBooksContainer = document.getElementById("allBooks");
    if (!books || books.length === 0) {
        recentlyAddedContainer.innerHTML = '<p>No books found.</p>';
        allBooksContainer.innerHTML = '<p>No books found.</p>';
        return;
    }
    // Recently added (first 6 books by latest id)
    const sortedBooks = [...books].sort((a, b) => b.id - a.id);
    recentlyAddedContainer.innerHTML = sortedBooks.slice(0, 6).map(createBookCard).join("");
    allBooksContainer.innerHTML = sortedBooks.map(createBookCard).join("");

    // Attach click event listeners to book cards after rendering
    document.querySelectorAll(".book-card").forEach((card) => {
        card.addEventListener('click', function() {
            const bookId = card.getAttribute('data-book-id');
            if (bookId) {
                window.location.href = `/book/${bookId}`;
            }
        });
    });
}


// Search functionality (if searchInput exists)
const searchInput = document.getElementById("searchInput");
if (searchInput) {
    searchInput.addEventListener("input", function (e) {
        const query = e.target.value.toLowerCase();
        const filteredBooks = books.filter(
            (book) =>
                book.title.toLowerCase().includes(query) ||
                book.author.toLowerCase().includes(query) ||
                (book.category && book.category.toLowerCase().includes(query))
        );
        document.getElementById("allBooks").innerHTML = filteredBooks.map(createBookCard).join("");
    });
}


// Alphabet filter
document.querySelectorAll(".alphabet-filter").forEach((button) => {
    button.addEventListener("click", function () {
        const letter = this.getAttribute("data-letter");
        document.querySelectorAll(".alphabet-filter").forEach((btn) => btn.classList.remove("bg-purple-500", "text-white"));
        this.classList.add("bg-purple-500", "text-white");
        let filteredBooks = books;
        if (letter !== "ALL") {
            filteredBooks = books.filter((book) => book.title.charAt(0).toUpperCase() === letter);
        }
        document.getElementById("allBooks").innerHTML = filteredBooks.map(createBookCard).join("");
    });
});


function showBookSpinner() {
    const spinner = document.getElementById('book-loading-spinner');
    if (spinner) spinner.style.display = 'flex';
}

function hideBookSpinner() {
    const spinner = document.getElementById('book-loading-spinner');
    if (spinner) spinner.style.display = 'none';
}

// Show content after all data is loaded
async function initializePage() {

    // Show spinner overlay
    showBookSpinner();

    // Fetch all required data
    await Promise.all([
        fetchDashboardStats(),
        fetchBooks()
    ]);
    console.log('All data fetched successfully');

    // Hide spinner overlay
    if (window.hideBookSpinner) window.hideBookSpinner();
}

initializePage();

// Add some interactive animations and click-to-detail
document.addEventListener("DOMContentLoaded", function () {
    // Animate cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    });

    document.querySelectorAll(".book-card").forEach((card) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(20px)";
        card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
        observer.observe(card);
    });
});
