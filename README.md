# Library Management System

A full-stack Library Management System with a FastAPI + Supabase backend and a static HTML/CSS/JS frontend.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Backend Overview](#backend-overview)
- [Frontend Overview](#frontend-overview)
- [Running the Project](#running-the-project)
- [API & Features](#api--features)
- [Database Schema](#database-schema)
- [Customization](#customization)
- [License](#license)

---

## Project Structure

```
Library_Management_System/
│
├── backend/    # FastAPI backend, Supabase integration, REST APIs
├── frontend/   # Static frontend (HTML, CSS, JS, templates)
└── schema_supabase.sql  # Database schema
```

---

## Backend Overview

- Built with **FastAPI** and **Supabase** (PostgreSQL)
- Provides RESTful APIs for books, users, borrowing, fines, notifications, and more
- Automated fine system for overdue books
- Role-based access (students, teachers, librarians)
- See `backend/README.md` for full details

### Run the Backend

```sh
cd backend
uvicorn main:app --reload
```

- Configure `.env.local` with your Supabase credentials
- Install dependencies: `pip install fastapi uvicorn python-dotenv supabase`

---

## Frontend Overview

- Static HTML, CSS, and JavaScript
- Organized by feature (auth, books, dashboard, user, etc.)
- Responsive design for desktop and mobile
- Consumes backend REST APIs for all dynamic data
- See `frontend/README.md` for full details

### Run the Frontend

- If using FastAPI backend, static files and templates are served automatically
- Or, serve manually for development:
  ```sh
  cd frontend
  python -m http.server 8000
  ```

---

## API & Features

- User authentication (login/register)
- Book management (add, update, delete, browse)
- Borrowing and returning books
- Fine calculation and payment
- Notifications and user profile management
- Dashboard for statistics

See backend and frontend READMEs for endpoint and UI details.

---

## Database Schema

- Supabase (PostgreSQL) with tables for users, books, borrow, fines, notifications, etc.
- See `schema_supabase.sql` for schema details

---

## Customization

- Update frontend styles in `frontend/static/`
- Modify backend logic in `backend/api/`, `backend/services/`
- Extend database schema as needed

---

## License

This project is for educational purposes.
