# Backend - Library Management System

This folder contains the backend code for the Library Management System. The backend is built using FastAPI and integrates with Supabase for database operations. It provides RESTful APIs for managing books, users, borrowing, fines, notifications, and more.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup & Configuration](#setup--configuration)
- [API Endpoints](#api-endpoints)
- [Fine System](#fine-system)
- [Database Schema](#database-schema)
- [Implementation Flow](#implementation-flow)
- [Security Considerations](#security-considerations)
- [Usage Examples](#usage-examples)

---

## Project Structure

```
backend/
│
├── api/                # FastAPI routers for each domain (books, user, borrow, etc.)
│   ├── books.py
│   ├── borrow.py
│   ├── category.py
│   ├── fine.py
│   ├── librarian.py
│   ├── notifications.py
│   ├── record.py
│   └── user.py
│
├── core/               # Core utilities and configuration
│   ├── config.py
│   ├── supabase_client.py
│   └── user.py
│
├── models/             # Pydantic models and schema definitions
│   ├── book.py
│   ├── borrow.py
│   ├── record.py
│   ├── schema_models.py
│   └── user.py
│
├── schemas/            # Pydantic schemas for API validation
│
├── services/           # Business logic and database service functions
│   ├── book.py
│   └── ...
│
└── main.py             # FastAPI application entry point
```

---

## Setup & Configuration

1. **Environment Variables:**  
   Create a `.env.local` file in the root directory with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SECRET_KEY=your_secret_key
   ```

2. **Install Dependencies:**  
   ```
   pip install fastapi uvicorn python-dotenv supabase
   ```

3. **Run the Server:**  
   ```
   cd backend
   uvicorn main:app --reload
   ```

---

## API Endpoints

### Books
- `POST /addbook` - Add a new book
- `POST /updatebook/{book_id}` - Update book details
- `GET /api/books` - List all books
- `GET /api/books/{book_id}` - Get book details
- `DELETE /api/books/{book_id}/delete` - Delete a book

### Categories
- `POST /addcategory` - Add a new category
- `POST /updatecategory/{category_id}` - Update category
- `GET /api/categories` - List all categories

### Users
- `POST /register` - Register a new user (student, teacher, librarian)
- `POST /login` - User login
- `POST /signout` - User signout
- `GET /api/user/profile` - Get user profile

### Borrowing
- `POST /api/borrow/request` - Request to borrow a book
- `POST /api/borrow/approve` - Approve borrow request
- `POST /api/borrow/return` - Return a borrowed book

### Fines
- `GET /api/fines` - Get all fines with filters
- `GET /api/fines/{fine_id}` - Get specific fine
- `DELETE /api/fines/{fine_id}/delete` - Delete fine
- `POST /api/fines/{fine_id}/pay` - Mark fine as paid
- `POST /api/fines/update-overdue` - Update overdue fines for user(s)
- `POST /api/fines/finalize-on-return` - Finalize fine on book return
- `GET /api/fines/user/{user_id}/total` - Get user's total unpaid fines
- `POST /api/fines/daily-update` - Daily update for all overdue fines

### Notifications
- `GET /api/notifications` - List notifications
- `POST /api/notifications/{notif_id}/approve` - Approve notification (e.g., borrow request)

---

## Fine System

The fine system is fully automated and ensures users are fined for overdue books according to the following rules:

- **Loan Period:** 14 days from approval
- **Fine Rate:** 100 per day late
- **Calculation:** `max(0, (return_date - due_date).days * 100)`
- **No Grace Period:** Fine starts immediately after due date

**Automation:**
- Fines are recalculated on user login, borrow request, and daily via a cron job.
- Borrowing is blocked if the user has unpaid fines.
- Fine payment is handled via a dedicated endpoint.

For more details, see [FINE_SYSTEM_DOCUMENTATION.md](../FINE_SYSTEM_DOCUMENTATION.md).

---

## Database Schema

The backend uses Supabase (PostgreSQL) with the following main tables:

- **users**: All user accounts (students, teachers, librarians)
- **students**, **teachers**, **librarians**: Role-specific info
- **books**: Book records
- **book_online**, **book_offline**: Storage details for books
- **categories**: Book categories
- **borrow**: Borrow records (with due_date)
- **fines**: Fine records (amount, paid status, etc.)
- **notifications**: System and borrow notifications

See [schema_supabase.sql](../schema_supabase.sql) for full schema.

---

## Implementation Flow

### Book Approval
1. Librarian approves borrow request
2. System sets due_date (approval_date + 14 days)
3. Creates fine record with amount = 0
4. Updates borrow status to "approved"

### User Login
1. User logs in
2. System updates all overdue fines for the user

### New Borrow Request
1. User requests to borrow book
2. System updates overdue fines first
3. Checks for unpaid fines (blocks if any)

### Book Return
1. Book is marked as returned
2. System finalizes fine based on actual return date

---

## Security Considerations

- Only librarians can approve/reject requests
- Users can only see their own fines
- Fine updates are automatic and cannot be manually manipulated
- Payment status can only be updated through payment endpoint

---

## Usage Examples

**Check User's Total Fines**
```
GET /api/fines/user/123/total
```

**Pay a Fine**
```
POST /api/fines/456/pay
Content-Type: application/json
{
  "payment_method": "credit_card"
}
```

**Daily Maintenance**
```
POST /api/fines/daily-update
```

---

## Additional Documentation
- [schema_supabase.sql](../schema_supabase.sql) — Database schema

---

## License

This project is for educational purposes.
