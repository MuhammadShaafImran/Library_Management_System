document.addEventListener('DOMContentLoaded', function () {
    const mybooksList = document.getElementById('mybooks-list');
    async function fetchMyBooks() {
        const res = await fetch('/api/mybooks');
        const books = await res.json();
        console.log('My Books:', books);
        mybooksList.innerHTML = '';
        if (!books.length) {
            mybooksList.innerHTML = `<tr><td colspan="11" class="text-center text-gray-500 py-6">No borrowed books.</td></tr>`;
            return;
        }
        books.forEach(book => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 transition';
            // Avatar cell: cover image or first letter
            let avatarHtml = '';
            if (book.cover_image) {
                avatarHtml = `<img src="${book.cover_image}" alt="Cover" class="w-10 h-10 rounded-full object-cover border border-gray-300 shadow-sm">`;
            } else {
                const firstLetter = book.title && book.title.length > 0 ? book.title[0].toUpperCase() : '?';
                avatarHtml = `<div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-lg border border-gray-300 shadow-sm">${firstLetter}</div>`;
            }
            tr.innerHTML = `
                <td class="px-4 py-3 whitespace-nowrap">${avatarHtml}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.isbn || '-'}</td>
                <td class="px-4 py-3 whitespace-nowrap font-semibold text-gray-900">${book.title}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.author}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.category_name || '-'}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.language || '-'}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.publisher || '-'}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.published_year || '-'}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">
                    <span class="inline-block rounded-full px-2 py-1 text-xs font-semibold bg-red-100 text-red-700">
                        ${book.return_date || '-'}
                    </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                    <span class="inline-block rounded-full px-2 py-1 text-xs font-semibold ${book.status === 'approved' ? 'bg-green-100 text-green-700' : book.status === 'pending' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}">
                        ${book.status.charAt(0).toUpperCase() + book.status.slice(1)}
                    </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${book.librarian_name || '-'}</td>
            `;
            mybooksList.appendChild(tr);
        });
    }
    fetchMyBooks();
});
