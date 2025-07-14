
function toggleStorageFields() {
    const storageType = document.getElementById('storage_type').value;
    const onlineFields = document.getElementById('online_fields');
    const offlineFields = document.getElementById('offline_fields');

    if (storageType === 'online') {
        onlineFields.classList.remove('hidden');
        offlineFields.classList.add('hidden');
    } else {
        onlineFields.classList.add('hidden');
        offlineFields.classList.remove('hidden');
    }
}

async function populateCategories() {
    try {
        const res = await fetch('/api/categories');
        if (!res.ok) return;
        const categories = await res.json();
        const select = document.getElementById('category');
        select.innerHTML = '<option value="">Select Category</option>';
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            select.appendChild(option);
        });
    } catch (e) { /* handle error */ }
}

async function populateLibrarians() {
    try {
        const res = await fetch('/api/librarians/active');
        if (!res.ok) return;
        const librarians = await res.json();
        const select = document.getElementById('added_by');
        select.innerHTML = '<option value="">Select Librarian</option>';
        librarians.forEach(lib => {
            const option = document.createElement('option');
            option.value = lib.id;
            option.textContent = lib.name + ' (' + lib.email + ')';
            select.appendChild(option);
        });
    } catch (e) { /* handle error */ }
}

document.addEventListener('DOMContentLoaded', function () {
    toggleStorageFields();
    populateCategories();
    populateLibrarians();
});