// Format date from M/D/YYYY to 'Mon DD, YYYY' (e.g., 7/3/2025 -> Jul 3, 2025)
function formatDateMDYtoLong(dateStr) {
    if (!dateStr) return '-';
    const [year, month, day] = dateStr.split('-').map(Number);
    if (!year || !month || !day) return dateStr;
    const date = new Date(year, month - 1, day);
    return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
// profile.js 

// Password visibility toggle
const passwordToggles = document.querySelectorAll('.fa-eye');
passwordToggles.forEach(toggle => {
    toggle.addEventListener('click', function () {
        const passwordInput = this.closest('.relative').querySelector('input');
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });
});

// Add this script to handle status color
function setStatusColor(element, status) {
    element.classList.remove('text-green-600', 'text-red-600', 'text-orange-500');
    if (status === 'active') {
        element.classList.add('text-green-600');
    } else if (status === 'inactive') {
        element.classList.add('text-orange-500');
    } else if (status === 'banned') {
        element.classList.add('text-red-600');
    }
}

// Example usage after fetching profile data:
function updateStatusColors(profile) {
    if (profile.role === 'student') {
        setStatusColor(document.getElementById('info-status-std'), profile.status);
    } else if (profile.role === 'teacher') {
        setStatusColor(document.getElementById('info-status-tech'), profile.status);
    } else if (profile.role === 'librarian') {
        setStatusColor(document.getElementById('info-status-lib'), profile.status);
    } else {
        setStatusColor(document.getElementById('info-status-guest'), profile.status);
    }
}

// Form validation and submission
const form = document.querySelector('form');
const inputs = form.querySelectorAll('input, select');

inputs.forEach(input => {
    input.addEventListener('focus', function () {
        this.classList.add('ring-2', 'ring-purple-500', 'ring-opacity-50');
    });

    input.addEventListener('blur', function () {
        this.classList.remove('ring-2', 'ring-purple-500', 'ring-opacity-50');
    });
});

// Auto-resize textareas if any
const textareas = document.querySelectorAll('textarea');
textareas.forEach(textarea => {
    textarea.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});




// Fill the profile card (view-only info)
function fillProfileCard(user) {
    console.log('Filling profile card with user data:', user);
    if (document.getElementById('profile-name')) document.getElementById('profile-name').textContent = user.name || '-';
    if (document.getElementById('profile-role')) document.getElementById('profile-role').textContent = user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : '-';
    if (document.getElementById('profile-email')) document.getElementById('profile-email').textContent = user.email || '-';
    if (document.getElementById('profile-joined')) document.getElementById('profile-joined').textContent = user.joined ? formatDateMDYtoLong(user.joined) : '-';
    if (document.getElementById('profile-last-login')) document.getElementById('profile-last-login').textContent = user.last_login ? formatDateMDYtoLong(user.last_login) : '-';

    // Profile image: circle with first letter
    if (document.getElementById('profile-firstletter')) {
        const firstLetter = (user.name || 'U')[0].toUpperCase();
        const colors = ['#22223b', '#2d3142', '#1a1a2e', '#232946', '#282c34', '#22223b', '#212529'];
        const color = colors[Math.floor((user.name ? user.name.charCodeAt(0) : 0) % colors.length)];
        const imgSpan = document.getElementById('profile-firstletter');
        imgSpan.style.background = color;
        imgSpan.textContent = firstLetter;
    }

    // Hide all info blocks
    document.getElementById('profile-info-student').style.display = 'none';
    document.getElementById('profile-info-teacher').style.display = 'none';
    document.getElementById('profile-info-librarian').style.display = 'none';
    document.getElementById('profile-info-guest').style.display = 'none';

    // Show and fill the correct info block
    if (user.role === 'student') {
        document.getElementById('profile-info-student').style.display = '';
        document.getElementById('info-rollno').textContent = user.rollno || '-';
        document.getElementById('info-department-std').textContent = user.department || '-';
        document.getElementById('info-batch').textContent = user.batch || '-';
        document.getElementById('info-semester').textContent = user.semester || '-';
        document.getElementById('info-status-std').textContent = user.status || '-';
    } else if (user.role === 'teacher') {
        document.getElementById('profile-info-teacher').style.display = '';
        document.getElementById('info-department-tech').textContent = user.department || '-';
        document.getElementById('info-designation').textContent = user.designation || '-';
        document.getElementById('info-status-tech').textContent = user.status || '-';
    } else if (user.role === 'librarian') {
        document.getElementById('profile-info-librarian').style.display = '';
        document.getElementById('info-admin').textContent = user.admin ? 'Yes' : 'No';
        document.getElementById('info-status-lib').textContent = user.status;
    } else if (user.role === 'guest') {
        document.getElementById('profile-info-guest').style.display = '';
        document.getElementById('info-status-guest').textContent = user.status || '-';
    }
}

// Fill the profile form (editable fields)
function fillProfileForm(user) {
    if (document.querySelector('input[name="name"]')) document.querySelector('input[name="name"]').value = user.name || '';
    if (document.querySelector('input[name="email"]')) document.querySelector('input[name="email"]').value = user.email || '';
    if (document.querySelector('input[name="phone"]')) document.querySelector('input[name="phone"]').value = user.phone || '';
    if (document.querySelector('input[name="password"]')) document.querySelector('input[name="password"]').value = user.password || '';

    // Hide all role fields first
    document.getElementById('student-fields').style.display = 'none';
    document.getElementById('teacher-fields').style.display = 'none';
    document.getElementById('librarian-fields').style.display = 'none';
    document.getElementById('guest-fields').style.display = 'none';

    // Show and fill fields based on user type
    if (user.role === 'student') {
        document.getElementById('student-fields').style.display = '';
        document.querySelector('input[name="rollno"]').value = user.rollno || '';
        document.querySelector('input[name="department"]').value = user.department || '';
        document.querySelector('input[name="batch"]').value = user.batch || '';
        document.querySelector('input[name="semester"]').value = user.semester || '';
    } else if (user.role === 'teacher') {
        document.getElementById('teacher-fields').style.display = '';
        document.querySelector('#teacher-fields input[name="department"]').value = user.department || '';
        document.querySelector('input[name="designation"]').value = user.designation || '';
    } else if (user.role === 'librarian') {
        document.getElementById('librarian-fields').style.display = '';
        document.querySelector('select[name="admin"]').value = user.admin ? 'true' : 'false';
    } else if (user.role === 'guest') {
        document.getElementById('guest-fields').style.display = '';
        document.querySelector('select[name="status"]').value = user.status || 'inactive';
    }
}

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

// Add toast animation keyframes to the page if not present
if (!document.getElementById('toast-keyframes')) {
    const style = document.createElement('style');
    style.id = 'toast-keyframes';
    style.innerHTML = `
    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes fadeOut { to { opacity: 0; } }
    `;
    document.head.appendChild(style);
}

// Fetch user info from FastAPI backend and populate the form and profile card
async function fetchAndFillUserProfile() {
    try {
        const res = await fetch('/api/user/profile');
        if (!res.ok) throw new Error('Failed to fetch user info');
        const data = await res.json();
        const user = data.user || {};
        console.log('Fetched user profile:', user);
        fillProfileForm(user);
        fillProfileCard(user);
        updateStatusColors(user);
        showToast({ type: 'info', message: 'Profile loaded successfully.' });
    } catch (err) {
        if (document.getElementById('profile-name')) document.getElementById('profile-name').textContent = 'No User';
        if (document.getElementById('profile-role')) document.getElementById('profile-role').textContent = '-';
        if (document.getElementById('profile-joined')) document.getElementById('profile-joined').textContent = '-';
        if (document.getElementById('profile-last-login')) document.getElementById('profile-last-login').textContent = '-';
        showToast({ type: 'error', message: 'Could not load user profile.' });
        console.error('Error fetching user profile:', err);
    }
}

// Call fetchAndFillUserProfile on DOMContentLoaded
document.addEventListener('DOMContentLoaded', fetchAndFillUserProfile);

// Store the original password when profile is loaded
let originalPassword = '';

function setOriginalPasswordFromUser(user) {
    // Only set if input exists
    const pwInput = document.querySelector('input[name="password"]');
    if (pwInput) {
        originalPassword = user.password || '';
    }
}

// Patch fillProfileForm to also set originalPassword
const _fillProfileForm = fillProfileForm;
fillProfileForm = function(user) {
    _fillProfileForm(user);
    setOriginalPasswordFromUser(user);
};

// Password check helper
function checkPasswordChangeAndMatch() {
    const pwInput = document.querySelector('input[name="password"]');
    const confirmInput = document.querySelector('input[name="confirm_password"]');
    if (!pwInput || !confirmInput) return { valid: true, changed: false };
    const pw = pwInput.value;
    const confirm = confirmInput.value;
    if (pw !== confirm) {
        return { valid: false, changed: false, reason: 'Passwords do not match.' };
    }
    if (pw !== originalPassword) {
        return { valid: true, changed: true };
    }
    return { valid: true, changed: false };
}

// Handle form submission to update profile via FastAPI backend
if (form) {
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Password check
        const pwCheck = checkPasswordChangeAndMatch();
        if (!pwCheck.valid) {
            showToast({ type: 'error', message: pwCheck.reason || 'Passwords do not match.' });
            return;
        }

        // Gather form data
        const formData = new FormData(form);

        // Append role field based on visible section
        if (document.getElementById('student-fields').style.display !== 'none') {
            formData.append('role', 'student');
        } else if (document.getElementById('teacher-fields').style.display !== 'none') {
            formData.append('role', 'teacher');
        } else if (document.getElementById('librarian-fields').style.display !== 'none') {
            formData.append('role', 'librarian');
        } else if (document.getElementById('guest-fields').style.display !== 'none') {
            formData.append('role', 'guest');
        }

        try {
            const response = await fetch('/api/user/profile', {
                method: 'POST',
                body: formData  // No need to set Content-Type
            });
            if (!response.ok) throw new Error('Failed to update profile');
            showToast({ type: 'success', message: pwCheck.changed ? 'Profile and password updated successfully.' : 'Your changes have been saved successfully.' });
            fetchAndFillUserProfile();
        } catch (err) {
            showToast({ type: 'error', message: 'Failed to save changes. Please try again.' });
        }
    });
}
