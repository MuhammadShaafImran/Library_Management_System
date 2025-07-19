# Frontend - Library Management System

This folder contains the frontend code for the Library Management System. The frontend is built using HTML, CSS, and JavaScript, and is organized by feature for maintainability and scalability. It provides user interfaces for authentication, book management, borrowing, user profiles, notifications, and dashboards.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup & Usage](#setup--usage)
- [Features](#features)
- [Pages & Components](#pages--components)
- [Styling](#styling)
- [API Integration](#api-integration)
- [Security Considerations](#security-considerations)
- [Customization](#customization)

---

## Project Structure

```
frontend/
│
├── static/
│   ├── styles.css                # Global styles
│   ├── auth/                     # Authentication JS
│   │   ├── login.js
│   │   └── register.js
│   ├── base/                     # Base layout styles and scripts
│   │   ├── base.css
│   │   └── base.js
│   ├── books/                    # Book-related JS and CSS
│   │   ├── addbooks.js
│   │   ├── book.css
│   │   ├── book.js
│   │   ├── lending.js
│   │   └── mybooks.js
│   ├── dashboard/                # Dashboard scripts and styles
│   │   ├── dashboard.css
│   │   └── dashboard.js
│   ├── home/                     # Home page scripts and styles
│   │   ├── home.css
│   │   └── home.js
│   └── user/                     # User profile, notifications, managers
│       ├── managers.js
│       ├── notification.js
│       ├── profile.css
│       └── profile.js
│
├── templates/
│   ├── base.html                 # Base template
│   ├── error.html                # Error page
│   ├── sidenavbar.html           # Sidebar navigation
│   ├── test.html                 # Test template
│   ├── auth/                     # Auth pages
│   │   ├── login.html
│   │   └── register.html
│   ├── book/                     # Book-related pages
│   │   ├── add_books.html
│   │   ├── book.html
│   │   ├── category.html
│   │   ├── lending.html
│   │   └── mybooks.html
│   ├── dashboard/                # Dashboard page
│   │   └── dashboard.html
│   ├── home/                     # Home page
│   │   └── home.html
│   └── user/                     # User-related pages
│       ├── managers.html
│       ├── notification.html
│       └── profile.html
```

---

## Setup & Usage

1. **No Build Step Required:**
   - The frontend is static and does not require a build tool. Simply serve the files using any web server or integrate with the backend server's static file serving.

2. **Development:**
   - Edit HTML templates in `templates/`.
   - Edit JS and CSS in `static/` and its subfolders.

3. **Running Locally:**
   - If using FastAPI backend, static files and templates are served automatically.
   - Alternatively, use a simple HTTP server:
     ```
     cd frontend
     python -m http.server 8000
     ```

---

## Features

- User authentication (login/register)
- Book browsing, searching, and management
- Borrow and return books
- Fine and notification display
- User profile management
- Dashboard for statistics and quick actions
- Responsive design for desktop and mobile

---

## Pages & Components

- **Authentication:** Login and registration forms
- **Books:** Add, view, lend, and manage books
- **Categories:** Browse and filter by category
- **Borrowing:** Request and track borrowed books
- **Dashboard:** Overview of library activity
- **User:** Profile, notifications, and manager views
- **Navigation:** Sidebar and top navigation
- **Error Handling:** User-friendly error pages

---

## Styling

- Global styles in `static/styles.css`
- Feature-specific styles in respective folders (e.g., `book.css`, `dashboard.css`)
- Responsive layouts using CSS Flexbox and Grid

---

## API Integration

- All dynamic data is fetched from the backend via RESTful APIs (see backend README for endpoints)
- AJAX requests are made using JavaScript `fetch` API
- Authentication tokens (if any) are stored in browser storage (localStorage/sessionStorage)

---

## Security Considerations

- User input is validated on both frontend and backend
- Sensitive actions require authentication
- CSRF and XSS mitigations should be considered if deploying publicly

---

## Customization

- Update styles in CSS files for branding
- Modify templates for new features or layout changes
- Extend JavaScript modules for additional interactivity

---

## License

This project is for educational purposes.
