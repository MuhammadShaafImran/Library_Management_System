document.addEventListener('DOMContentLoaded', function () {
    const notificationsList = document.getElementById('notifications-list');
    async function fetchNotifications() {
        const res = await fetch('/api/notifications');
        const notifications = await res.json();
        console.log(notifications);
        notificationsList.innerHTML = '';
        if (!notifications.length) {
            notificationsList.innerHTML = '<tr><td colspan="6" class="text-center text-gray-500 py-4">No notifications.</td></tr>';
            return;
        }
        notifications.forEach(note => {
            const row = document.createElement('tr');
            row.className = 'border-b hover:bg-gray-50';
            // User avatar and name (placeholder avatar)
            let userCell = `<td class="py-3 px-4 flex items-center gap-2">
                <span class="inline-block w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold text-sm">
                    <i class="fas fa-user"></i>
                </span>
                <span>${note.user_name || ''}</span>
            </td>`;
            // Book title
            let bookCell = `<td class="py-3 px-4">${note.book_title || ''}</td>`;
            // Date
            let dateCell = `<td class="py-3 px-4">${note.created_at ? new Date(note.created_at).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''}</td>`;
            // Status
            let statusCell = `<td class="py-3 px-4">
                <span class="inline-block px-2 py-1 rounded text-xs font-semibold ${note.status === 'approved' ? 'bg-green-100 text-green-700' : note.status === 'rejected' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}">
                    ${note.status ? note.status.charAt(0).toUpperCase() + note.status.slice(1) : 'Pending'}
                </span>
            </td>`;
            // Action buttons
            let actionCell = `<td class="py-3 px-4 flex gap-2">`;
            if (note.action === 'Pending') {
                actionCell += `<button title="Approve" class="approve-btn bg-green-100 text-green-700 rounded-full p-2 hover:bg-green-200" data-id="${note.id}"><i class="fas fa-check"></i></button>`;
                actionCell += `<button title="Reject" class="reject-btn bg-red-100 text-red-700 rounded-full p-2 hover:bg-red-200" data-id="${note.id}"><i class="fas fa-times"></i></button>`;
            }
            actionCell += `</td>`;
            // Message
            let messageCell = `<td class="py-3 px-4">${note.message || ''}</td>`;
            // Compose row
            row.innerHTML = userCell + messageCell + bookCell + dateCell + statusCell + actionCell;
            notificationsList.appendChild(row);
        });

        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                console.log('Approving notification with ID:', id);
                fetch(`/api/notifications/${id}/approve`, { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            fetchNotifications();
                        } else {
                            alert('Failed: ' + (data.error || 'Unknown error'));
                        }
                    });
            });
        });
        document.querySelectorAll('.reject-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                alert('Reject action for notification id ' + id);
                fetch(`/api/notifications/${id}/reject`, { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            fetchNotifications();
                        } else {
                            alert('Failed: ' + (data.error || 'Unknown error'));
                        }
                    });
            });
        });
    }
    fetchNotifications();
});
