document.addEventListener('DOMContentLoaded', () => {
    // const addBookForm = document.getElementById('add-book-form');
    // const updateBookForm = document.getElementById('update-book-form');
    // const deleteBookForm = document.getElementById('delete-book-form');
    // const searchBooksForm = document.getElementById('search-books-form');
    // const borrowBookForm = document.getElementById('borrow-book-form');
    // const returnBookForm = document.getElementById('return-book-form');

    // addBookForm.addEventListener('submit', async (e) => {
    //     e.preventDefault();
    //     const title = document.getElementById('book-title').value;
    //     const author = document.getElementById('book-author').value;
    //     console.log(`Adding book: ${title} by ${author}`);
    //     fetch('/books', {
    //         method: 'POST',
    //         headers: { 'Content-Type': 'application/json' },
    //         body: JSON.stringify({ title, author })
    //     })
    //     .then(response => response.json())
    //     .then(data => console.log(data));
    // });
    
    // updateBookForm.addEventListener('submit', async (e) => {
    //     e.preventDefault();
    //     const bookId = document.getElementById('book-id').value;
    //     const title = document.getElementById('new-book-title').value;
    //     const author = document.getElementById('new-book-author').value;
    //     const response = await fetch(`/books/${bookId}`, {
    //         method: 'PUT',
    //         headers: { 'Content-Type': 'application/json' },
    //         body: JSON.stringify({ title, author })
    //     });
    //     const result = await response.json();
    //     alert(result.message);
    // });

    // deleteBookForm.addEventListener('submit', async (e) => {
    //     e.preventDefault();
    //     const bookId = document.getElementById('delete-book-id').value;
    //     const response = await fetch(`/books/${bookId}`, {
    //         method: 'DELETE'
    //     });
    //     const result = await response.json();
    //     alert(result.message);
    // });

    // searchBooksForm.addEventListener('submit', async (e) => {
    //     e.preventDefault();
    //     const query = document.getElementById('search-query').value;
    //     const response = await fetch(`/books?query=${query}`);
    //     const result = await response.json();
    //     alert(result.message);
    // });

    // borrowBookForm.addEventListener('submit', async (e) => {
    //     e.preventDefault();
    //     const bookId = document.getElementById('borrow-book-id').value;
    //     const borrowerName = document.getElementById('borrower-name').value;
    //     const response = await fetch('/borrow', {
    //         method: 'POST',
    //         headers: { 'Content-Type': 'application/json' },
    //         body: JSON.stringify({ bookId, borrowerName })
    //     });
    //     const result = await response.json();
    //     alert(result.message);
    // });

    // returnBookForm.addEventListener('submit', async (e) => {
    //     e.preventDefault();
    //     const bookId = document.getElementById('return-book-id').value;
    //     const response = await fetch('/return', {
    //         method: 'POST',
    //         headers: { 'Content-Type': 'application/json' },
    //         body: JSON.stringify({ bookId })
    //     });
    //     const result = await response.json();
    //     alert(result.message);
    // });

});
