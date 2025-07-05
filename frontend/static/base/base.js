
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

// Initialize header height
setHeaderHeightVar();
window.addEventListener('resize', setHeaderHeightVar);

function toggleSidebar() {
    sidebarOpen = !sidebarOpen;

    if (sidebarOpen) {
        // Open sidebar
        sidebar.classList.add('open');
        sidebarOverlay.classList.remove('hidden');

        // Hide mobile search bar
        if (mobileSearch) {
            mobileSearch.classList.add('mobile-search-hidden');
        }

        // Change hamburger to X
        mobileMenuBtn.innerHTML = '<i class="fas fa-times text-2xl"></i>';
    } else {
        // Close sidebar
        sidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');

        // Show mobile search bar
        if (mobileSearch) {
            mobileSearch.classList.remove('mobile-search-hidden');
        }

        // Change X to hamburger
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';
    }
}

// Event listeners
if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', toggleSidebar);
}

if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', toggleSidebar);
}

// Close sidebar when clicking on sidebar links (mobile)
const sidebarLinks = document.querySelectorAll('.sidebar-item');
sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth < 640 && sidebarOpen) {
            toggleSidebar();
        }
    });
});

// Handle window resize
window.addEventListener('resize', function () {
    if (window.innerWidth >= 640) {
        // Reset everything for desktop
        sidebarOpen = false;
        sidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars text-2xl"></i>';

        // Show mobile search bar (it will be hidden by CSS on desktop anyway)
        if (mobileSearch) {
            mobileSearch.classList.remove('mobile-search-hidden');
        }
    }
});

// Prevent body scroll when sidebar is open on mobile
function toggleBodyScroll() {
    if (sidebarOpen && window.innerWidth < 640) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Update toggle function to include body scroll prevention
const originalToggle = toggleSidebar;
toggleSidebar = function () {
    originalToggle();
    toggleBodyScroll();
};