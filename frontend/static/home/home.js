// Sample book data
const books = [
    {
        id: 1,
        title: "The Great Gatsby",
        author: "F. Scott Fitzgerald",
        genre: "Classic Literature",
        rating: 4.5,
        pages: 180,
        year: 1925,
        color: "from-yellow-400 to-orange-500",
    },
    {
        id: 2,
        title: "To Kill a Mockingbird",
        author: "Harper Lee",
        genre: "Fiction",
        rating: 4.8,
        pages: 281,
        year: 1960,
        color: "from-blue-400 to-purple-500",
    },
    {
        id: 3,
        title: "1984",
        author: "George Orwell",
        genre: "Dystopian Fiction",
        rating: 4.7,
        pages: 328,
        year: 1949,
        color: "from-red-400 to-pink-500",
    },
    {
        id: 4,
        title: "Pride and Prejudice",
        author: "Jane Austen",
        genre: "Romance",
        rating: 4.6,
        pages: 432,
        year: 1813,
        color: "from-green-400 to-blue-500",
    },
    {
        id: 5,
        title: "The Catcher in the Rye",
        author: "J.D. Salinger",
        genre: "Coming-of-age Fiction",
        rating: 4.3,
        pages: 234,
        year: 1951,
        color: "from-purple-400 to-pink-500",
    },
    {
        id: 6,
        title: "Lord of the Flies",
        author: "William Golding",
        genre: "Adventure Fiction",
        rating: 4.4,
        pages: 224,
        year: 1954,
        color: "from-orange-400 to-red-500",
    },
    {
        id: 7,
        title: "The Hobbit",
        author: "J.R.R. Tolkien",
        genre: "Fantasy",
        rating: 4.9,
        pages: 310,
        year: 1937,
        color: "from-green-400 to-teal-500",
    },
    {
        id: 8,
        title: "Harry Potter and the Philosopher's Stone",
        author: "J.K. Rowling",
        genre: "Fantasy",
        rating: 4.8,
        pages: 223,
        year: 1997,
        color: "from-indigo-400 to-purple-500",
    },
    {
        id: 9,
        title: "The Da Vinci Code",
        author: "Dan Brown",
        genre: "Mystery Thriller",
        rating: 4.2,
        pages: 454,
        year: 2003,
        color: "from-yellow-400 to-orange-600",
    },
    {
        id: 10,
        title: "The Alchemist",
        author: "Paulo Coelho",
        genre: "Philosophical Fiction",
        rating: 4.5,
        pages: 163,
        year: 1988,
        color: "from-blue-400 to-cyan-500",
    },
];

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
        stars += '<i class="far fa-star text-gray-300"></i>';
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
    const truncatedTitle =
        book.title.length > 20 ? book.title.slice(0, 20) + "..." : book.title;
    const truncatedGenre =
        book.genre.length > 10 ? book.genre.slice(0, 10) + "..." : book.genre;
    return `
                <div class="book-card p-4 transition-all">
                    <!-- image page -->
                    <div class="book-cover bg-gray-100 rounded-lg h-48 mb-4 flex items-center justify-center relative overflow-hidden">
                        <div class="absolute inset-0 bg-black/10"></div>
                        <div class="text-white text-center z-10">
                            <h3 class="font-bold text-lg mb-1" title="${book.title
        }">${truncatedTitle}</h3>
                            <p class="text-sm opacity-90">${book.author}</p>
                        </div>
                    </div>
                    <!-- information -->
                    <div class="space-y-2">
                        <div class="flex justify-between items-start">
                            <div>
                                <h4 class="font-semibold text-gray-800 text-sm" title="${book.title
        }">${truncatedTitle}</h4>
                                <p class="text-gray-600 text-xs">${book.author
        }</p>
                            </div>
                            <div class="flex items-center space-x-1">
                                <span class="text-xs font-medium text-gray-700">${book.rating
        }</span>
                            </div>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs" style="color: ${genreToColor(
            book.genre
        )}" title="${book.genre}">${truncatedGenre}</span>
                            <span class="text-xs text-gray-500">${book.pages
        } pages</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <div class="flex space-x-1">
                                ${generateStars(book.rating)}
                            </div>
                            <span class="text-xs text-gray-500">${book.year
        }</span>
                        </div>
                    </div>
                </div>
            `;
}

// Populate books
function populateBooks() {
    const recentlyAddedContainer = document.getElementById("recentlyAdded");
    const allBooksContainer = document.getElementById("allBooks");

    // Recently added (first 6 books)
    recentlyAddedContainer.innerHTML = books
        .slice(0, 6)
        .map((book) => createBookCard(book))
        .join("");

    // All books
    allBooksContainer.innerHTML = books
        .map((book) => createBookCard(book))
        .join("");
}

// Search functionality
document.getElementById("searchInput").addEventListener("input", function (e) {
    const query = e.target.value.toLowerCase();
    const filteredBooks = books.filter(
        (book) =>
            book.title.toLowerCase().includes(query) ||
            book.author.toLowerCase().includes(query) ||
            book.genre.toLowerCase().includes(query)
    );

    document.getElementById("allBooks").innerHTML = filteredBooks
        .map((book) => createBookCard(book))
        .join("");
});

// Alphabet filter
document.querySelectorAll(".alphabet-filter").forEach((button) => {
    button.addEventListener("click", function () {
        const letter = this.getAttribute("data-letter");

        // Update active state
        document
            .querySelectorAll(".alphabet-filter")
            .forEach((btn) => btn.classList.remove("bg-purple-500", "text-white"));
        this.classList.add("bg-purple-500", "text-white");

        // Filter books
        let filteredBooks = books;
        if (letter !== "ALL") {
            filteredBooks = books.filter(
                (book) => book.title.charAt(0).toUpperCase() === letter
            );
        }

        document.getElementById("allBooks").innerHTML = filteredBooks
            .map((book) => createBookCard(book))
            .join("");
    });
});

// Initialize
populateBooks();

// Add some interactive animations
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
