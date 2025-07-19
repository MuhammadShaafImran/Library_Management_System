// Toast Notification System
function showToast({ type = 'info', title = '', message = '' }) {
    // Ensure toast container has a high z-index and is properly positioned
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-50 space-y-3 w-80';
        document.body.appendChild(toastContainer);
    } else {
        // Ensure the container is visible and correctly styled
        toastContainer.style.zIndex = '9999';
        toastContainer.style.position = 'fixed';
        toastContainer.style.top = '1rem';
        toastContainer.style.right = '1rem';
    }

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
    const toast = document.createElement('div');
    toast.className = `toast flex items-start p-4 ${c.bg} rounded-lg border ${c.border} shadow-lg animate-slideIn`;
    toast.style.animation = 'slideIn 0.5s forwards, fadeOut 0.5s forwards 3s';
    toast.style.opacity = '1'; // Ensure opacity is set to visible
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
    }, 3000);
}

if (!document.getElementById('toast-keyframes')) {
    const style = document.createElement('style');
    style.id = 'toast-keyframes';
    style.innerHTML = `
    @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes fadeOut { to { opacity: 0; } }
    `;
    document.head.appendChild(style);
}

// Login form AJAX handler
document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(loginForm);
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });
                if (response.redirected) {
                    showToast({ type: 'success', message: 'Login successful! Redirecting...' });
                    setTimeout(() => { window.location.href = response.url; }, 1200);
                } else {
                    let res = null;
                    try {
                        res = await response.json();
                    } catch (err) {
                        showToast({ type: 'error', message: 'Unexpected server error.' });
                        return;
                    }

                    if (res?.error) {
                        showToast({ type: 'error', message: res.error });
                    } else {
                        showToast({ type: 'error', message: 'Incorrect email or password.' });
                    }
                }
            } catch (err) {
                showToast({ type: 'error', message: 'An error occurred during login.' });
            }
        });
    }
});