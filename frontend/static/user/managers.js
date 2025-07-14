document.addEventListener('DOMContentLoaded', function () {
    const librariansList = document.getElementById('librarians-list');
    async function fetchLibrarians() {
        const res = await fetch('/api/librarians');
        const librarians = await res.json();
        librariansList.innerHTML = '';
        if (!librarians.length) {
            librariansList.innerHTML = `<tr><td colspan="5" class="text-center text-gray-500 py-6">No librarians found.</td></tr>`;
            return;
        }
        librarians.forEach(librarian => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 transition';
            // Avatar cell: first letter of name
            const firstLetter = librarian.name && librarian.name.length > 0 ? librarian.name[0].toUpperCase() : '?';
            const avatarHtml = `<div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-lg border border-gray-300 shadow-sm">${firstLetter}</div>`;
            tr.innerHTML = `
                <td class="px-4 py-3 whitespace-nowrap">${avatarHtml}</td>
                <td class="px-4 py-3 whitespace-nowrap font-semibold text-gray-900">${librarian.name}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${librarian.email}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${librarian.phone || '-'}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${librarian.joining_date}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${librarian.last_login}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">
                    <span class="inline-block rounded-full px-2 py-1 text-xs font-semibold ${librarian.admin ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                        ${librarian.admin ? 'Yes' : 'No'}
                    </span>
                </td>
            `;
            librariansList.appendChild(tr);
        });
    }
    fetchLibrarians();
});
