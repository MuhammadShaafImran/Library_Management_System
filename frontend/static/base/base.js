// Sidebar mobile toggle functionality
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const header = document.getElementById('main-header');
const mobileSearch = document.getElementById('mobile-search');
let sidebarOpen = false;

// Set header height as CSS variable for sidebar padding
function setHeaderHeightVar() {
    if (header) {
        const headerHeight = header.offsetHeight;
        document.documentElement.style.setProperty('--header-height', headerHeight + 'px');
    }
}

setHeaderHeightVar();
window.addEventListener('resize', setHeaderHeightVar);

function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
    if (sidebarOpen) {
        sidebar.classList.add('open');
        sidebarOverlay.classList.remove('hidden');
        if (mobileSearch) mobileSearch.classList.add('mobile-search-hidden');
        mobileMenuBtn.innerHTML = '<i class="fas fa-times text-2xl"></i>';
    } else {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');
        if (mobileSearch) mobileSearch.classList.remove('mobile-search-hidden');
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';
    }
}

if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', toggleSidebar);
if (sidebarOverlay) sidebarOverlay.addEventListener('click', toggleSidebar);

// Close sidebar when clicking on sidebar links (mobile)
document.querySelectorAll('.sidebar-item').forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth < 640 && sidebarOpen) toggleSidebar();
    });
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.innerWidth >= 640) {
        sidebarOpen = false;
        sidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';
        if (mobileSearch) mobileSearch.classList.remove('mobile-search-hidden');
    }
});

// Prevent body scroll when sidebar is open on mobile
function toggleBodyScroll() {
    document.body.style.overflow = (sidebarOpen && window.innerWidth < 640) ? 'hidden' : '';
}

const originalToggle = toggleSidebar;
toggleSidebar = function () {
    originalToggle();
    toggleBodyScroll();
};

// Smooth navbar shadow on scroll
document.addEventListener('scroll', () => {
    const header = document.getElementById('main-header');
    if (window.scrollY > 8) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Profile dropdown and signout
document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('profile-dropdown-btn');
    const dropdown = document.getElementById('profile-dropdown');
    const container = document.getElementById('profile-dropdown-container');
    if (btn && dropdown) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', function (e) {
            if (!container.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });
    }
    // Signout logic
    const signoutBtn = document.getElementById('signout-btn');
    if (signoutBtn) {
        signoutBtn.addEventListener('click', function () {
            fetch('/signout', { method: 'POST' })
                .then(() => { window.location.href = '/login'; });
        });
    }
});

// Search bar logic
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchInputMobile = document.getElementById('searchInputMobile');
    const searchDropdown = document.getElementById('searchDropdown');
    const mobileSearchDropdown = document.getElementById('mobileSearchDropdown');
    const searchResultsList = document.getElementById('searchResultsList');
    const mobileSearchResultsList = document.getElementById('mobileSearchResultsList');

    function createSearchResultItem(book) {
        const listItem = document.createElement('li');
        listItem.className = 'search-result-item rounded-lg hover:bg-gray-50 transition-colors';

        const linkWrapper = document.createElement('a');
        linkWrapper.href = `/book/${book.id}`;
        linkWrapper.className = 'flex items-center space-x-3 p-3 w-full block text-decoration-none';
        linkWrapper.style.textDecoration = 'none';

        const coverContainer = document.createElement('div');
        coverContainer.className = 'flex-shrink-0';

        const cover = document.createElement('img');
        cover.src = book.cover_image || '/static/images/default-book-cover.jpg';
        cover.alt = book.title;
        cover.className = 'w-12 h-16 rounded-md object-cover border border-gray-200';
        cover.onerror = function () {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA0OCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yNCAxNlYzMk0xNiAyNEgzMiIgc3Ryb2tlPSIjOUI5QkExIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K';
        };
        coverContainer.appendChild(cover);

        const info = document.createElement('div');
        info.className = 'flex-1 min-w-0';

        const title = document.createElement('p');
        title.className = 'font-medium text-gray-900 truncate';
        title.textContent = book.title;

        const author = document.createElement('p');
        author.className = 'text-sm text-gray-500 truncate';
        author.textContent = book.author;

        info.appendChild(title);
        info.appendChild(author);

        if (book.categories && book.categories.length > 0) {
            const category = document.createElement('p');
            category.className = 'text-xs text-blue-600 truncate';
            category.textContent = book.categories.map(cat => cat.name).join(', ');
            info.appendChild(category);
        }

        const arrowIcon = document.createElement('div');
        arrowIcon.className = 'flex-shrink-0 text-gray-400';
        arrowIcon.innerHTML = '<i class="fas fa-chevron-right text-sm"></i>';

        linkWrapper.appendChild(coverContainer);
        linkWrapper.appendChild(info);
        linkWrapper.appendChild(arrowIcon);
        listItem.appendChild(linkWrapper);
        return listItem;
    }

    function performSearch(query, isMobile = false) {
        const dropdown = isMobile ? mobileSearchDropdown : searchDropdown;
        const resultsList = isMobile ? mobileSearchResultsList : searchResultsList;
        if (query.length > 1) {
            fetch(`/api/books/search?query=${encodeURIComponent(query)}&limit=8`)
                .then(response => response.json())
                .then(data => {
                    resultsList.innerHTML = '';
                    if (data.books && data.books.length > 0) {
                        data.books.forEach(book => {
                            const listItem = createSearchResultItem(book);
                            resultsList.appendChild(listItem);
                        });
                        if (data.books.length === 8) {
                            const viewAllItem = document.createElement('li');
                            viewAllItem.className = 'border-t border-gray-200 mt-2 pt-2';
                            const viewAllLink = document.createElement('a');
                            viewAllLink.href = `/books?search=${encodeURIComponent(query)}`;
                            viewAllLink.className = 'flex items-center justify-center space-x-2 p-3 text-blue-600 hover:bg-blue-50 rounded-lg font-medium transition-colors';
                            viewAllLink.innerHTML = '<i class="fas fa-search mr-2"></i>View all results';
                            viewAllItem.appendChild(viewAllLink);
                            resultsList.appendChild(viewAllItem);
                        }
                    } else {
                        const noResults = document.createElement('li');
                        noResults.className = 'p-3 text-center text-gray-500';
                        noResults.innerHTML = '<div class="flex flex-col items-center space-y-2"><i class="fas fa-search text-gray-300 text-2xl"></i><span>No books found</span></div>';
                        resultsList.appendChild(noResults);
                    }
                    dropdown.classList.remove('hidden');
                })
                .catch(error => {
                    console.error('Search error:', error);
                    resultsList.innerHTML = '<li class="p-3 text-center text-red-500">Error loading results</li>';
                    dropdown.classList.remove('hidden');
                });
        } else {
            dropdown.classList.add('hidden');
        }
    }

    // Desktop search functionality
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            if (searchInputMobile) searchInputMobile.value = query;
            performSearch(query, false);
        });
        searchInput.addEventListener('focus', () => {
            const query = searchInput.value.trim();
            if (query.length > 2) searchDropdown.classList.remove('hidden');
        });
    }

    // Mobile search functionality
    if (searchInputMobile) {
        searchInputMobile.addEventListener('input', () => {
            const query = searchInputMobile.value.trim();
            if (searchInput) searchInput.value = query;
            performSearch(query, true);
        });
        searchInputMobile.addEventListener('focus', () => {
            const query = searchInputMobile.value.trim();
            if (query.length > 2) mobileSearchDropdown.classList.remove('hidden');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', e => {
        if (searchDropdown && !searchDropdown.contains(e.target) && e.target !== searchInput) {
            searchDropdown.classList.add('hidden');
        }
        if (mobileSearchDropdown && !mobileSearchDropdown.contains(e.target) && e.target !== searchInputMobile) {
            mobileSearchDropdown.classList.add('hidden');
        }
    });

    // Prevent dropdowns from closing when clicking inside them
    if (searchDropdown) {
        searchDropdown.addEventListener('click', e => e.stopPropagation());
    }
    if (mobileSearchDropdown) {
        mobileSearchDropdown.addEventListener('click', e => e.stopPropagation());
    }
});