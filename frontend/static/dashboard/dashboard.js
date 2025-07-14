// Tab functionality
const tabButtons = document.querySelectorAll('.tab-button-custom');
const tabContents = document.querySelectorAll('.tab-content');
const loading = document.getElementById('loading');
const tabUnderline = document.getElementById('tab-underline');

// Fetch data from backend APIs
let dashboardStats = {};
let booksData = [];
let categoriesData = [];
let borrowersData = [];
let finesData = [];

async function fetchDashboardStats() {
    const res = await fetch('/api/dashboard/stats');
    dashboardStats = await res.json();
    console.log(dashboardStats);
}

async function fetchBooks() {
    const res = await fetch('/api/books');
    console.log(res);
    booksData = await res.json();
    console.log('Books data:', booksData);
}

async function fetchCategories() {
    const res = await fetch('/api/categories');
    categoriesData = await res.json();
    console.log('Categories data:', categoriesData);
}

async function fetchBorrowers() {
    const res = await fetch('/api/borrowers');
    borrowersData = await res.json();
    console.log('Borrowers data:', borrowersData);
}

async function fetchFines() {
    const res = await fetch('/api/fines');
    finesData = await res.json();
    console.log('Fines data:', finesData);
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async function () {
    tabButtons[0].classList.add('active');
    setUnderline();

    // Show loading spinner
    loading.classList.remove('hidden');
    // Hide all tab contents while loading
    tabContents.forEach(content => content.classList.add('hidden'));

    await fetchDashboardStats();
    await fetchBooks();
    await fetchCategories();
    await fetchBorrowers();
    // await fetchFines();

    updateStats();
    loadBooksData();

    // Hide loading spinner and show first tab
    loading.classList.add('hidden');
    tabContents[0].classList.remove('hidden');

    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            setUnderline();

            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    window.addEventListener('resize', setUnderline);
});

function setUnderline() {
    const active = document.querySelector('.tab-button-custom.active');
    if (active) {
        const nav = active.parentElement;
        const navRect = nav.getBoundingClientRect();
        const btnRect = active.getBoundingClientRect();
        tabUnderline.style.width = btnRect.width + 'px';
        tabUnderline.style.left = (btnRect.left - navRect.left) + 'px';
    }
}

function switchTab(tabName) {
    // Show loading
    loading.classList.remove('hidden');

    // Hide all tab contents
    tabContents.forEach(content => {
        content.classList.add('hidden');
    });

    // Remove active class from all buttons
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });

    // Add active class to clicked button
    const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
    activeButton.classList.add('active');

    // Simulate loading delay
    setTimeout(() => {
        loading.classList.add('hidden');

        // Show selected tab content
        const selectedTab = document.getElementById(tabName);
        selectedTab.classList.remove('hidden');
        selectedTab.classList.add('slide-in');

        // Load data for the selected tab
        switch (tabName) {
            case 'books':
                loadBooksData();
                break;
            case 'categories':
                loadCategoriesData();
                break;
            case 'borrowers':
                loadBorrowersData();
                break;
            case 'fines':
                loadFinesData();
                break;
        }
    }, 500);
}

function updateStats() {
    document.getElementById('total-books').textContent = dashboardStats.total_books || 0;
    document.getElementById('active-borrowers').textContent = dashboardStats.active_borrowers || 0;
    document.getElementById('total-categories').textContent = dashboardStats.total_categories || 0;
    document.getElementById('pending-fines').textContent = (dashboardStats.pending_fines || 0).toFixed(2);

    // Show additional info if available (assume backend can provide *_last_month fields)
    // Fallback to 0 if not present
    const booksLast = dashboardStats.total_books_last_month || 0;
    const booksNow = dashboardStats.total_books || 0;
    const booksDiff = booksNow - booksLast;
    document.getElementById('books-diff-info').textContent = `${booksDiff >= 0 ? '+' : ''}${booksDiff} from last month`;

    const borrowersLast = dashboardStats.active_borrowers_last_month || 0;
    const borrowersNow = dashboardStats.active_borrowers || 0;
    const borrowersDiff = borrowersNow - borrowersLast;
    document.getElementById('borrowers-diff-info').textContent = `${borrowersDiff >= 0 ? '+' : ''}${borrowersDiff} from last month`;

    const categoriesLast = dashboardStats.total_categories_last_month || 0;
    const categoriesNow = dashboardStats.total_categories || 0;
    const categoriesDiff = categoriesNow - categoriesLast;
    document.getElementById('categories-diff-info').textContent = `${categoriesDiff >= 0 ? '+' : ''}${categoriesDiff} new categories`;

    const finesLast = dashboardStats.pending_fines_last_month || 0;
    const finesNow = dashboardStats.pending_fines || 0;
    let finesDiffPercent = 0;
    if (finesLast !== 0) {
        finesDiffPercent = ((finesNow - finesLast) / Math.abs(finesLast) * 100).toFixed(1);
    }
    document.getElementById('fines-diff-info').textContent = `${finesDiffPercent >= 0 ? '+' : ''}${finesDiffPercent}% change from last month`;
}

function loadBooksData() {
    const booksList = document.getElementById('books-list');
    booksList.innerHTML = '';
    booksData.forEach((book, index) => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors slide-in';
        row.style.animationDelay = `${index * 0.1}s`;
        row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-center">
                    ${book.cover_image
                ? `<img src="${book.cover_image}" alt="Cover" class="w-14 h-14 object-cover rounded-full shadow-md mx-auto">`
                : '<div class="w-14 h-14 bg-gray-200 rounded-full flex items-center justify-center text-gray-400 text-sm mx-auto">N/A</div>'}
                </td>
                <td class="px-4 py-2 text-sm font-bold text-blue-900 text-center">${book.title}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.author}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.category}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.isbn || ''}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.language || ''}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.platform_name !== null ? book.platform_name : 'N/A'}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.published_year || ''}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${book.publisher || ''}</td>
                <td class="px-4 py-2 text-center">
                    <span class="inline-block px-2 py-1 rounded text-xs font-semibold bg-green-100 text-green-800">${book.quantity ?? 'N/A'}</span>
                </td>
                <td class="px-4 py-2 text-center">
                    <span class="inline-block px-2 py-1 rounded text-xs font-semibold bg-yellow-100 text-yellow-800">${book.rating !== undefined ? book.rating : 'N/A'}</span>
                </td>
                <td class="px-4 py-2 text-center">
                    <span class="inline-block px-2 py-1 rounded-full text-xs font-semibold bg-blue-200 text-blue-800">${book.storage_type || 'N/A'}</span>
                </td>
                <td class="px-4 py-2 text-sm font-medium whitespace-nowrap text-center">
                    <button class="edit-book-btn mr-3" data-book-id="${book.id}" data-category-name="${book.category || ''}" title="Edit">
                        <i class="fas fa-pen text-blue-500 hover:text-blue-700"></i>
                    </button>
                    <button class="delete-book-btn" data-book-id="${book.id}" data-book-title="${book.title}" title="Delete">
                        <i class="fas fa-trash text-red-500 hover:text-red-700"></i>
                    </button>
                </td>
            `;
        booksList.appendChild(row);
    });

    // Add event listeners for edit and delete buttons
    document.querySelectorAll('.edit-book-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const bookId = this.getAttribute('data-book-id');
            // Redirect to add-book with book_id as query param (no need for category_name)
            window.location.href = `/add-book?book_id=${bookId}`;
        });
    });
    document.querySelectorAll('.delete-book-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const bookId = this.getAttribute('data-book-id');
            const bookTitle = this.getAttribute('data-book-title');
            if (confirm(`Are you sure you want to delete the book "${bookTitle}"? This action cannot be undone.`)) {
                fetch(`/api/books/${bookId}/delete`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast({ type: 'success', message: 'Book deleted successfully!' });
                            fetchBooks().then(loadBooksData);
                        } else {
                            showToast({ type: 'error', message: 'Failed to delete book: ' + (data.error || 'Unknown error') });
                        }
                    })
                    .catch(() => showToast({ type: 'error', message: 'Failed to delete book.' }));
            }
        });
    });
}

function loadCategoriesData() {
    const categoriesGrid = document.getElementById('categories-grid');
    categoriesGrid.innerHTML = '';

    categoriesData.forEach((category, index) => {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-lg shadow-md p-6 card-hover slide-in';
        card.style.animationDelay = `${index * 0.1}s`;
        card.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                        <i class="fas fa-tag text-white"></i>
                    </div>
                    <div class="text-right">
                        <button class="text-blue-600 hover:text-blue-900 mr-3 hover-grow edit-category-btn" data-category-id="${category.id}">Edit</button>
                        <button class="text-red-600 hover:text-red-900 hover-grow delete-category-btn" data-category-id="${category.id}" data-category-name="${category.name}">Delete</button>
                    </div>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">${category.name}</h3>
                <p class="text-gray-600 text-sm mb-4">${category.description}</p>
                <div class="flex items-center justify-between">
                    <span class="text-2xl font-bold text-gray-900">${category.book_count}</span>
                    <span class="text-sm text-gray-500">books</span>
                </div>
            `;
        categoriesGrid.appendChild(card);
    });

    // Add event listeners for edit and delete buttons
    document.querySelectorAll('.edit-category-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const categoryId = this.getAttribute('data-category-id');
            window.location.href = `/add-category?category_id=${categoryId}`;
        });
    });
    document.querySelectorAll('.delete-category-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const categoryId = this.getAttribute('data-category-id');
            const categoryName = this.getAttribute('data-category-name');
            if (confirm(`Are you sure you want to delete the category "${categoryName}"? This action cannot be undone.`)) {
                fetch(`/api/categories/${categoryId}/delete`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast({ type: 'success', message: 'Category deleted successfully!' });
                            fetchCategories().then(loadCategoriesData);
                        } else {
                            showToast({ type: 'error', message: 'Failed to delete category: ' + (data.error || 'Unknown error') });
                        }
                    })
                    .catch(() => showToast({ type: 'error', message: 'Failed to delete category.' }));
            }
        });
    });
}

function loadBorrowersData() {
    const borrowersList = document.getElementById('borrowers-list');
    borrowersList.innerHTML = '';

    // Build a map of book_id to book title for quick lookup
    const bookMap = {};
    if (Array.isArray(booksData)) {
        booksData.forEach(book => {
            if (book.id) bookMap[book.id] = book.title;
        });
    }

    // Optionally, build a map of admin id to name if you have that data
    // For now, just show the id or blank

    // Helper for date formatting (MDY to 'Mon DD, YYYY')
    function formatDateMDYtoLong(dateStr) {
        if (!dateStr) return '-';
        const [year, month, day] = dateStr.split('-').map(Number);
        if (!year || !month || !day) return dateStr;
        const date = new Date(year, month - 1, day);
        return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }

    borrowersData.forEach((borrower, index) => {
        const statusClass = borrower.borrow_status === 'approved' ? 'status-active' :
            borrower.borrow_status === 'pending' ? 'status-pending' :
                borrower.borrow_status === 'rejected' ? 'status-overdue' : 'bg-gray-100 text-gray-800';

        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors slide-in';
        row.style.animationDelay = `${index * 0.1}s`;
        row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="w-14 h-14 bg-gray-200 rounded-full flex items-center justify-center text-gray-400 text-sm mx-auto capitalize">${borrower.user_type[0] || 'U'}</div>
                </td>
                <td class="px-4 py-2 text-sm text-gray-700 text-blue-900 text-center">${borrower.email}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${borrower.rollno ?? ''}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${bookMap[borrower.book_id] ?? borrower.book_id ?? ''}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${borrower.batch ?? ''}</td>
                <td class="px-4 py-2 text-sm text-gray-700 text-center">${borrower.department ?? ''}</td>
                <td class="px-4 py-2 text-center">
                    <span class="inline-block px-2 py-1 rounded text-xs font-semibold bg-green-100 text-green-800">${borrower.books_borrowed ?? ''}</span>
                </td>
                <td class="px-4 py-2 text-xs text-gray-700 text-center">${borrower.return_date ? formatDateMDYtoLong(borrower.return_date) : ''}</td>
                <td class="px-4 py-2 text-center">
                    <span class="inline-block px-2 py-1 rounded-full text-xs font-semibold ${statusClass}">${borrower.borrow_status ?? ''}</span>
                </td>
                <td class="px-4 py-2 text-center">${borrower.reminder_sent ? '<i class=\"fas fa-check text-green-500\"></i>' : '<i class=\"fas fa-times text-red-500\"></i>'}</td>
                <td class="px-4 py-2 text-xs text-gray-700 text-center">${borrower.approved_by ?? ''}</td>
                <td class="px-4 py-2 text-sm font-medium whitespace-nowrap text-center">
                    <button class="edit-borrower-btn mr-3" data-borrower-id="${borrower.id}" title="Edit">
                        <i class="fas fa-pen text-blue-500 hover:text-blue-700"></i>
                    </button>
                    <button class="delete-borrower-btn" data-borrower-id="${borrower.id}" data-borrower-name="${borrower.name}" title="Delete">
                        <i class="fas fa-trash text-red-500 hover:text-red-700"></i>
                    </button>
                </td>
            `;
        borrowersList.appendChild(row);
    });

    // Add event listeners for edit and delete buttons
    document.querySelectorAll('.edit-borrower-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const borrowerId = this.getAttribute('data-borrower-id');
            window.location.href = `/profile?borrower_id=${borrowerId}`;
        });
    });
    document.querySelectorAll('.delete-borrower-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const borrowerId = this.getAttribute('data-borrower-id');
            const borrowerName = this.getAttribute('data-borrower-name');
            if (confirm(`Are you sure you want to delete the borrower "${borrowerName}"? This action cannot be undone.`)) {
                fetch(`/api/borrowers/${borrowerId}/delete`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast({ type: 'success', message: 'Borrower deleted successfully!' });
                            fetchBorrowers().then(loadBorrowersData);
                        } else {
                            showToast({ type: 'error', message: 'Failed to delete borrower: ' + (data.error || 'Unknown error') });
                        }
                    })
                    .catch(() => showToast({ type: 'error', message: 'Failed to delete borrower.' }));
            }
        });
    });
}

function loadFinesData() {
    const finesList = document.getElementById('fines-list');
    finesList.innerHTML = '';

    finesData.forEach((fine, index) => {
        let status = 'Unpaid';
        if (fine.paid) status = 'Paid';
        const statusClass = status === 'Paid' ? 'status-paid' :
            status === 'Unpaid' ? 'status-unpaid' : 'status-pending';

        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors slide-in';
        row.style.animationDelay = `${index * 0.1}s`;
        row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${fine.borrower_name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${fine.book_title}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${fine.amount.toFixed(2)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${fine.reason || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="status-badge ${statusClass} border rounded-full text-sm px-2 py-1">${status}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-green-600 hover:text-green-900 mr-3 hover-grow mark-paid-btn" data-fine-id="${fine.id}">Mark Paid</button>
                    <button class="text-blue-600 hover:text-blue-900 hover-grow delete-fine-btn" data-fine-id="${fine.id}" data-fine-title="${fine.book_title}">Delete</button>
                </td>
            `;
        finesList.appendChild(row);
    });

    // Add event listeners for mark paid and delete buttons
    document.querySelectorAll('.mark-paid-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const fineId = this.getAttribute('data-fine-id');
            if (confirm('Mark this fine as paid?')) {
                fetch(`/api/fines/${fineId}/mark-paid`, { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast({ type: 'success', message: 'Fine marked as paid!' });
                            fetchFines().then(loadFinesData);
                        } else {
                            showToast({ type: 'error', message: 'Failed to mark fine as paid: ' + (data.error || 'Unknown error') });
                        }
                    })
                    .catch(() => showToast({ type: 'error', message: 'Failed to mark fine as paid.' }));
            }
        });
    });
    document.querySelectorAll('.delete-fine-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const fineId = this.getAttribute('data-fine-id');
            const fineTitle = this.getAttribute('data-fine-title');
            if (confirm(`Are you sure you want to delete the fine for "${fineTitle}"? This action cannot be undone.`)) {
                fetch(`/api/fines/${fineId}/delete`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast({ type: 'success', message: 'Fine deleted successfully!' });
                            fetchFines().then(loadFinesData);
                        } else {
                            showToast({ type: 'error', message: 'Failed to delete fine: ' + (data.error || 'Unknown error') });
                        }
                    })
                    .catch(() => showToast({ type: 'error', message: 'Failed to delete fine.' }));
            }
        });
    });
}

// Add some interactive features
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('hover-grow')) {
        e.target.style.transform = 'scale(0.95)';
        setTimeout(() => {
            e.target.style.transform = 'scale(1)';
        }, 100);
    }
});

// Toast Notification System
function showToast({ type = 'info', title = '', message = '' }) {
    // Ensure toast container exists
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-50 space-y-3 w-80';
        document.body.appendChild(toastContainer);
    }

    // Toast type config
    const config = {
        success: {
            bg: 'bg-green-50',
            border: 'border-green-100',
            icon: `<svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>`,
            title: title || 'Success',
        },
        error: {
            bg: 'bg-red-50',
            border: 'border-red-100',
            icon: `<svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>`,
            title: title || 'Error',
        },
        warning: {
            bg: 'bg-yellow-50',
            border: 'border-yellow-100',
            icon: `<svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>`,
            title: title || 'Warning',
        },
        info: {
            bg: 'bg-indigo-50',
            border: 'border-indigo-100',
            icon: `<svg class="w-5 h-5 text-indigo-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>`,
            title: title || 'Info',
        },
    };
    const c = config[type] || config.info;

    // Toast element
    const toast = document.createElement('div');
    toast.className = `toast flex items-start p-4 ${c.bg} rounded-lg border ${c.border} shadow-lg animate-slideIn`;
    toast.style.animation = 'slideIn 0.5s forwards, fadeOut 0.5s forwards 3s';
    toast.innerHTML = `
        <div class="flex-shrink-0">${c.icon}</div>
        <div class="ml-3">
            <h3 class="text-sm font-medium ${type === 'success' ? 'text-green-800' : type === 'error' ? 'text-red-800' : type === 'warning' ? 'text-yellow-800' : 'text-indigo-800'}">${c.title}</h3>
            <p class="mt-1 text-sm ${type === 'success' ? 'text-green-600' : type === 'error' ? 'text-red-600' : type === 'warning' ? 'text-yellow-600' : 'text-indigo-600'}">${message}</p>
        </div>
        <button class="ml-auto ${type === 'success' ? 'text-green-400 hover:text-green-500' : type === 'error' ? 'text-red-400 hover:text-red-500' : type === 'warning' ? 'text-yellow-400 hover:text-yellow-500' : 'text-indigo-400 hover:text-indigo-500'}" aria-label="Close toast" onclick="this.parentElement.remove()">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
    `;
    toastContainer.prepend(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}