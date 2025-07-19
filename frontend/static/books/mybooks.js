function showBookSpinner() {
  const spinner = document.getElementById("book-loading-spinner");
  if (spinner) spinner.style.display = "flex";
}

function hideBookSpinner() {
  const spinner = document.getElementById("book-loading-spinner");
  if (spinner) spinner.style.display = "none";
}

async function fetchMyBooks() {
  const mybooksList = document.getElementById("mybooks-list");
  const res = await fetch("/api/mybooks");
  const books = await res.json();
  console.log("My Books:", books);
  mybooksList.innerHTML = "";
  if (!books.length) {
    mybooksList.innerHTML = `<tr><td colspan="11" class="text-center text-gray-500 py-6">No borrowed books.</td></tr>`;
    return;
  }
  books.forEach((book) => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-gray-50 transition";
    // Avatar cell: cover image or first letter
    let avatarHtml = "";
    if (book.cover_image) {
      avatarHtml = `<img src="${book.cover_image}" alt="Cover" class="w-10 h-10 rounded-full object-cover border border-gray-300 shadow-sm">`;
    } else {
      const firstLetter =
        book.title && book.title.length > 0 ? book.title[0].toUpperCase() : "?";
      avatarHtml = `<div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-lg border border-gray-300 shadow-sm">${firstLetter}</div>`;
    }
    // Status color logic
    let statusColor = "";
    if (book.status === "rejected") {
      statusColor = "bg-red-100 text-red-700";
    } else if (book.status === "returned") {
      statusColor = "bg-orange-100 text-orange-700";
    } else if (book.status === "approved") {
      statusColor = "bg-green-100 text-green-700";
    } else {
      statusColor = "bg-yellow-100 text-yellow-700";
    }
    // Only show return button if not returned
    let returnBtn = "";
    if (book.status === "approved") {
      returnBtn = `<td class="px-4 py-3 whitespace-nowrap text-green-700 return-book-btn" data-book-id="${book.id}" style="cursor:pointer;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="m20 10 .354.354.353-.354-.353-.354zM3.5 18a.5.5 0 0 0 1 0zm11.854-2.646 5-5-.708-.708-5 5zm5-5.708-5-5-.708.708 5 5zM20 9.5H10v1h10zM3.5 16v2h1v-2zM10 9.5A6.5 6.5 0 0 0 3.5 16h1a5.5 5.5 0 0 1 5.5-5.5z" fill="#1E90FF"/>
            </svg>
        </td>`;
    } else {
      returnBtn =
        `<td class="px-4 py-3 whitespace-nowrap text-gray-400">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="m5 14 4 3 9-11" stroke="#D3D3D3" stroke-width="2"/>
            </svg>
        </td>`;
    }
    tr.innerHTML = `
                <td class="px-4 py-3 whitespace-nowrap">${avatarHtml}</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${
                  book.isbn || "-"
                }</td>
                <td class="px-4 py-3 whitespace-nowrap font-semibold text-gray-900">${
                  book.title
                }</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${
                  book.author
                }</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${
                  book.category_name || "-"
                }</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${
                  book.publisher || "-"
                }</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">
                    <span class="inline-block rounded-full px-2 py-1 text-xs font-semibold bg-red-100 text-red-700">
                        ${book.return_date || "-"}
                    </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                    <span class="inline-block rounded-full px-2 py-1 text-xs font-semibold ${statusColor}">
                        ${
                          book.status.charAt(0).toUpperCase() +
                          book.status.slice(1)
                        }
                    </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">${
                  book.librarian_name || "-"
                }</td>
                <td class="px-4 py-3 whitespace-nowrap text-gray-700">
                    <span class="inline-block rounded-full px-2 py-1 text-xs font-semibold bg-sky-100 text-sky-700">
                        ${book.fine_amount || "0"}
                    </span>
                </td>
                ${returnBtn}
            `;
    // Add event listener for return button only if not returned
    if (book.status !== "returned") {
      tr.querySelector(".return-book-btn").addEventListener("click", () => {
        let bookId = book.book_id || book.id || book.isbn || null;
        if (!bookId) {
          bookId = tr
            .querySelector(".return-book-btn")
            .getAttribute("data-book-id");
        }
        document.getElementById("return-book-id").value = bookId;
        document.getElementById("return_description").value = "";
        document.getElementById("borrow-return").classList.remove("hidden");
      });
    }
    mybooksList.appendChild(tr);
  });
}

// Modal logic for return

document
  .getElementById("close-return-modal")
  .addEventListener("click", function () {
    document.getElementById("borrow-return").classList.add("hidden");
  });

document
  .getElementById("borrow-return-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();
    // Get bookId from hidden input instead of data attribute
    const bookId = document.getElementById("return-book-id").value;
    const returnCondition = document
      .getElementById("return_description")
      .value.trim();

    // Convert and validate bookId

    if (!bookId || isNaN(bookId)) {
      console.error("Invalid book ID:", bookIdRaw);
      alert("Invalid book ID. Please try again.");
      return;
    }

    if (!returnCondition) {
      alert("Please enter the return condition.");
      return;
    }
    showBookSpinner();
    try {
      const res = await fetch("/api/borrow/update_return_condition", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          book_id: bookId,
          return_condition: returnCondition,
        }),
      });
      const data = await res.json();
      if (data.success) {
        alert(data.message || "Return submitted successfully.");
        document.getElementById("borrow-return").classList.add("hidden");
        await fetchMyBooks();
      } else {
        alert(data.error || "Failed to submit return.");
      }
    } catch (err) {
      alert("Error submitting return.");
    }
    hideBookSpinner();
  });

document.addEventListener("DOMContentLoaded", async function () {
  showBookSpinner();
  await fetchMyBooks();
  hideBookSpinner();
});
