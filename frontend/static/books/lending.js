document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-books');
    const booksList = document.getElementById('books-list');
    let books = [];

    async function fetchBooks(query = '') {
        let url = '/api/books';
        if (query) url += `?search=${encodeURIComponent(query)}`;
        const res = await fetch(url);
        books = await res.json();
        console.log(books);
        renderBooks();
    }

    function renderBooks() {
        booksList.innerHTML = '';
        if (!books.length) {
            booksList.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500 py-4">No books found.</td></tr>';
            return;
        }
        books.forEach(book => {
            let avatarHtml = '';
            if (book.cover_image) {
                avatarHtml = `<img src="${book.cover_image}" alt="Cover" class="w-10 h-10 rounded-full object-cover border border-gray-300 shadow-sm">`;
            } else {
                const firstLetter = book.title && book.title.length > 0 ? book.title[0].toUpperCase() : '?';
                avatarHtml = `<div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-lg border border-gray-300 shadow-sm">${firstLetter}</div>`;
            }
            const row = document.createElement('tr');
            row.className = 'border-b hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-4 py-3 whitespace-nowrap">${avatarHtml}</td>
                <td class="px-4 py-2">${book.isbn || ''}</td>
                <td class="px-4 py-2 font-medium text-gray-900">${book.title}</td>
                <td class="px-4 py-2">${book.author}</td>
                <td class="px-4 py-2">${book.category || ''}</td>
                <td class="px-4 py-2">${book.language || ''}</td>
                <td class="px-4 py-2">${book.publisher || ''}</td>
                <td class="px-4 py-2">${book.published_year || ''}</td>
                <td class="px-4 py-2">
                    <span class="inline-block bg-${book.quantity === 0 ? 'red' : 'green'}-100 text-${book.quantity === 0 ? 'red' : 'green'}-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                        ${book.quantity === 0 ? 'Not Available' : 'Available'}
                    </span>
                </td>
                <td class="px-4 py-2">
                    <button class="request-borrow-btn" data-book-id="${book.id}" ${book.quantity === 0 ? 'disabled' : ''} title="Borrow">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="inline align-middle ${book.quantity === 0 ? 'opacity-50' : 'hover:scale-110 transition-transform'}">
                          <path d="M18 16H6a2 2 0 0 0-2 2v0a2 2 0 0 0 2 2h12" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <path d="M18 16V3H7a3 3 0 0 0-3 3v12m13-2v4" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </td>
            `;
            booksList.appendChild(row);
        });

        // Modal logic
        const borrowModal = document.getElementById('borrow-modal');
        const closeModalBtn = document.getElementById('close-modal');
        const borrowForm = document.getElementById('borrow-form');
        const modalBookId = document.getElementById('modal-book-id');
        const requestDescription = document.getElementById('request_description');
        const returnDate = document.getElementById('return_date');
        const userSelect = document.getElementById('user_select');

        // Fetch users for dropdown (no search)
        async function fetchUsers() {
            let url = '/api/users/all';
            const res = await fetch(url);
            const users = await res.json();
            userSelect.innerHTML = '';
            users.forEach(user => {
                const opt = document.createElement('option');
                opt.value = user.id;
                opt.textContent = `${user.name} (${user.email})`;
                userSelect.appendChild(opt);
            });
        }

        // Only fetch once on modal open
        document.querySelectorAll('.request-borrow-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const bookId = this.getAttribute('data-book-id');
                modalBookId.value = bookId;
                requestDescription.value = '';
                returnDate.value = '';
                fetchUsers();
                borrowModal.classList.remove('hidden');
            });
        });

        closeModalBtn.addEventListener('click', function () {
            borrowModal.classList.add('hidden');
        });

        borrowForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const bookId = modalBookId.value;
            const desc = requestDescription.value.trim();
            const date = returnDate.value;
            const userId = userSelect.value;
            if (!desc || !date || !userId) {
                alert('Please fill in all fields.');
                return;
            }
            fetch('/api/borrow/admin_request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    book_id: bookId,
                    request_description: desc,
                    return_date: date,
                    user_id: userId
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Borrow request sent!');
                        borrowModal.classList.add('hidden');
                        fetchBooks(searchInput.value);
                    } else {
                        alert('Failed to request: ' + (data.error || 'Unknown error'));
                    }
                });
        });
    }

    // Use base.html search bar
    const baseSearchInput = document.getElementById('searchInput');
    const baseSearchInputMobile = document.getElementById('searchInputMobile');

    if (baseSearchInput) {
        baseSearchInput.addEventListener('input', function () {
            fetchBooks(this.value);
        });
    }
    if (baseSearchInputMobile) {
        baseSearchInputMobile.addEventListener('input', function () {
            fetchBooks(this.value);
        });
    }

    // Remove old search bar if present
    const oldSearchBar = document.getElementById('search-books');
    if (oldSearchBar) oldSearchBar.parentElement.style.display = 'none';

    fetchBooks();
});
