from fastapi import FastAPI, Request, Query, status, Form, Response, HTTPException, Depends, Cookie, Path
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from dotenv import load_dotenv
from enum import Enum
import os
import json

from supabase import create_client, Client

# --- App and Middleware ---
app = FastAPI(title="Library Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend/static/"), name="static")
templates = Jinja2Templates(directory="../frontend/templates/")

# --- Environment and Supabase ---
load_dotenv(dotenv_path='../.env.local')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_supabase_client() -> Client | None:
    if SUPABASE_KEY and SUPABASE_URL:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None
# --- Enums ---
class UserType(str, Enum):
    student = "student"
    teacher = "teacher"
    librarian = "librarian"
    guest = "guest"

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"

class StorageType(str, Enum):
    online = "online"
    offline = "offline"

class BorrowStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# --- Pydantic Models ---
class DashboardStats(BaseModel):
    total_books: int
    total_books_last_month: int
    active_borrowers: int
    active_borrowers_last_month: int
    total_categories: int
    total_categories_last_month: int
    pending_fines: float
    pending_fines_last_month: float

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category_name: str
    storage_type: str
    isbn: Optional[str]
    publisher: str
    published_year: int
    language: str
    cover_image: Optional[str]
    quantity: Optional[int] = None
    access_url: Optional[str] = None
    platform_name: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: date
    book_count: int

class BorrowerResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: str
    phone: Optional[str]
    status: str
    last_login: Optional[date]
    joining_date: date
    books_borrowed: int
    department: Optional[str] = None
    rollno: Optional[int] = None
    batch: Optional[int] = None
    semester: Optional[int] = None
    designation: Optional[str] = None


# --- Session Helpers ---
def get_session_data(request: Request):
    cookie = request.cookies.get("session")
    if not cookie:
        return {}
    try:
        data = serializer.loads(cookie, max_age=3600)
        return data
    except Exception:
        return {}

def set_session_data(response: Response, data: dict):
    session_cookie = serializer.dumps(data)
    response.set_cookie(
        key="session",
        value=session_cookie,
        httponly=True,
        samesite="lax"
    )

def clear_session(response: Response):
    response.delete_cookie("session")

# --- HTML Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request):
    session = get_session_data(request)
    name = session.get('name') or "U"
    context = {"request": request, 'name': name, 'firstletter': name[0]}
    return templates.TemplateResponse("dashboard/dashboard.html", context)

@app.get('/register', response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("auth/signUp.html", {"request": request})

@app.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("auth/signIn.html", {"request": request})

@app.get("/user/profile", response_class=HTMLResponse)
async def get_user_profile(request: Request):
    session = get_session_data(request)
    if not session:
        return templates.TemplateResponse("error.html", {'request': request})
    try:
        user = session
        extra = {}
        if user.get('type') == 'student':
            extra = supabase.table('students').select('*').eq('id', user['id']).single().execute().data
        elif user.get('type') == 'teacher':
            extra = supabase.table('teachers').select('*').eq('id', user['id']).single().execute().data
        elif user.get('type') == 'librarian':
            extra = supabase.table('librarians').select('*').eq('id', user['id']).single().execute().data
        profile = {
            "name": user.get('name'),
            "email": user.get('email'),
            "role": user.get('type'),
            "joined": user.get('joining_date'),
            "phone": user.get('phone'),
            "status": user.get('status'),
            "last_login": user.get('last_login'),
        }
        if extra:
            for key, value in extra.items():
                profile[key] = value
        context = {'request': request, "user": profile}
        return templates.TemplateResponse("profile.html", context)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Add/Edit Category Page (pre-fill if category_id is provided)
@app.get('/add-category', response_class=HTMLResponse)
async def add_category_page(request: Request, category_id: Optional[int] = Query(None)):
    session = get_session_data(request)
    name = session.get('name') or "U"
    category = None
    if category_id:
        supabase = get_supabase_client()
        if supabase:
            resp = supabase.table("categories").select("*").eq("id", category_id).single().execute()
            if resp.data:
                category = resp.data
    context = {"request": request, 'name': name, 'firstletter': name[0], 'category': category}
    return templates.TemplateResponse("book/category.html", context)

@app.get('/add-book', response_class=HTMLResponse)
async def add_book_page(request: Request, book_id: Optional[int] = Query(None)):
    session = get_session_data(request)
    name = session.get('name') or "U"
    book = {}
    if book_id:
        supabase = get_supabase_client()
        if supabase:
            # Fetch book details
            book_resp = supabase.table("books").select("*", "book_offline(*)", "book_online(*)").eq("id", book_id).single().execute()
            if book_resp.data:
                book = book_resp.data
                # Flatten book_offline/book_online if present
                if book.get('book_offline'):
                    book.update(book['book_offline'])
                if book.get('book_online'):
                    book.update(book['book_online'])
    context = {"request": request, 'name': name, 'firstletter': name[0], 'book': book}
    return templates.TemplateResponse("book/add_books.html", context)

@app.get('/home')
def loadhomePage(request: Request):
    session = get_session_data(request)
    name = session.get('name') or "U"
    context = {"request": request, 'name': name, 'firstletter': name[0]}
    return templates.TemplateResponse("home/home.html", context)

# --- API Endpoints ---
@app.get("/me")
def me(request: Request):
    session = get_session_data(request)
    if session:
        return {"user": session}
    return {"error": "Not logged in"}

@app.delete("/api/books/{book_id}/delete")
async def delete_book(book_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"success": False, "error": "Supabase client not found."}

        # Delete from book_offline and book_online if exists
        supabase.table("book_offline").delete().eq("id", book_id).execute()
        supabase.table("book_online").delete().eq("id", book_id).execute()
        # Delete the book itself
        result = supabase.table("books").delete().eq("id", book_id).execute()
        if result.data:
            return {"success": True}
        else:
            return {"success": False, "error": "Book not found or could not be deleted."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/user/profile")
def get_user_profile_api(request: Request):
    session = get_session_data(request)
    if not session:
        return {"success": False}
    try:
        user = session
        extra = {}
        if user.get('type') == 'student':
            extra = supabase.table('students').select('*').eq('id', user['id']).single().execute().data
        elif user.get('type') == 'teacher':
            extra = supabase.table('teachers').select('*').eq('id', user['id']).single().execute().data
        elif user.get('type') == 'librarian':
            extra = supabase.table('librarians').select('*').eq('id', user['id']).single().execute().data
        profile = {
            "name": user.get('name'),
            "email": user.get('email'),
            "role": user.get('type'),
            "joined": user.get('joining_date'),
            "phone": user.get('phone'),
            "status": user.get('status'),
            "last_login": user.get('last_login'),
        }
        if extra:
            for key, value in extra.items():
                profile[key] = value
        return {"user": profile}
    except Exception as e:
        return {"error": str(e)}

@app.post("/addcategory")
async def add_category(
    category_name: str = Form(...),
    category_description: str = Form(...)
):
    try:
        if not category_name or not category_description:
            return JSONResponse(status_code=400, content={"error": "Category name and description are required."})
        today = datetime.now().date().isoformat()
        result = supabase.table("categories").insert({
            "name": category_name,
            "description": category_description,
            "created_at": today
        }).execute()
        if not result.data:
            return JSONResponse(status_code=500, content={"error": "Failed to add category."})
        return RedirectResponse(url="/add-book", status_code=302)
    except Exception as e:
        print("Error adding category:", str(e))
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post('/login')
def login_user(email: str = Form(...), password: str = Form(...)):
    if not email or not password:
        return {"error": "Email and password are required"}, 400
    try:
        user_data = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
        if not user_data.data:
            return {"error": "Invalid email or password"}, 401
        supabase.table('users').update({"last_login": datetime.now().isoformat()}).eq('email', email).execute()
        redirect_response = RedirectResponse(url="/home", status_code=302)
        set_session_data(redirect_response, user_data.data[0])
        return redirect_response
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/registerForm")
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    type: str = Form(...),
    phone: Optional[str] = Form(None),
    roll_no: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    batch: Optional[str] = Form(None),
    semester: Optional[str] = Form(None),
    teacher_department: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    admin: Optional[bool] = Form(False),
):
    try:
        if not name or not email or not password:
            return JSONResponse(status_code=400, content={"error": "Name, email, and password are required"})
        existing_user = supabase.table('users').select('email').eq('email', email).execute()
        if existing_user.data:
            return JSONResponse(status_code=400, content={"error": "Email already exists"})
        today = datetime.now().isoformat()
        newUser = supabase.table('users').insert({
            "name": name,
            "email": email,
            "password": password,
            "type": type,
            "phone": phone,
            "status": "active",
            "last_login": today,
            "joining_date": today
        }).execute()
        ID = newUser.data[0]['id']
        if type == "student":
            if not all([roll_no, department, batch, semester]):
                return JSONResponse(status_code=400, content={"error": "Student info missing."})
            supabase.table('students').insert({
                "id": ID,
                "rollno": roll_no,
                "department": department,
                "batch": batch,
                "semester": semester
            }).execute()
        elif type == "teacher":
            if not all([teacher_department, designation]):
                return JSONResponse(status_code=400, content={"error": "Teacher info missing."})
            supabase.table('teachers').insert({
                "id": ID,
                "department": teacher_department,
                "designation": designation
            }).execute()
        elif type == "librarian":
            supabase.table('librarians').insert({
                "id": ID,
                "admin": admin
            }).execute()
        return RedirectResponse(url="/home", status_code=302)
    except Exception as e:
        print("Error during registration:", str(e))
        return JSONResponse(status_code=400, content={"error": str(e)})

# --- API: Dashboard, Books, Categories, Borrowers, Fines, Search ---
@app.get("/api/librarians", response_model=List[BorrowerResponse])
async def get_active_librarians():
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        # Fetch all users with type 'librarian' and status 'active'
        users_response = supabase.table("users").select("*").eq("type", "librarian").eq("status", "active").execute()
        librarians = []
        for user in users_response.data:
            librarians.append(BorrowerResponse(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                user_type=user["type"],
                phone=user.get("phone"),
                status=user["status"],
                last_login=user.get("last_login"),
                joining_date=user["joining_date"],
                books_borrowed=0,  # Not relevant for librarians
                department=user.get("department"),
                rollno=user.get("rollno"),
                batch=user.get("batch"),
                semester=user.get("semester"),
                designation=user.get("designation")
            ))
        return librarians
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # Current month
        books_response = supabase.table("books").select("id, created_at").execute()
        total_books = len(books_response.data)
        categories_response = supabase.table("categories").select("id,created_at").execute()
        total_categories = len(categories_response.data)
        active_borrowers_response = supabase.table("borrow").select("user_id, request_date,status").eq("status", "approved").execute()
        active_borrowers = len(set([b["user_id"] for b in active_borrowers_response.data]))
        pending_fines_response = supabase.table("fines").select("amount,created_at,paid").eq("paid", False).execute()
        pending_fines = sum(fine["amount"] for fine in pending_fines_response.data)
        today = datetime.now()
        first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)
        last_of_last_month = first_of_this_month - timedelta(seconds=1)

        # Books last month
        total_books_last_month = len([
            b for b in books_response.data
            if b.get("created_at") and first_of_last_month <= datetime.fromisoformat(b["created_at"].replace('Z','')) <= last_of_last_month
        ])
        # Categories last month
        total_categories_last_month = len([
            c for c in categories_response.data
            if c.get("created_at") and first_of_last_month <= datetime.fromisoformat(c["created_at"].replace('Z','')) <= last_of_last_month
        ])
        # Active borrowers last month
        active_borrowers_last_month = len(set([
            b["user_id"] for b in active_borrowers_response.data
            if b.get("borrowed_at") and first_of_last_month <= datetime.fromisoformat(b["borrowed_at"].replace('Z','')) <= last_of_last_month
        ]))
        # Pending fines last month
        pending_fines_last_month = sum([
            f["amount"] for f in pending_fines_response.data
            if f.get("created_at") and first_of_last_month <= datetime.fromisoformat(f["created_at"].replace('Z','')) <= last_of_last_month
        ])

        return DashboardStats(
            total_books=total_books,
            total_books_last_month=total_books_last_month,
            active_borrowers=active_borrowers,
            active_borrowers_last_month=active_borrowers_last_month,
            total_categories=total_categories,
            total_categories_last_month=total_categories_last_month,
            pending_fines=pending_fines,
            pending_fines_last_month=pending_fines_last_month
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books", response_model=List[BookResponse])
async def get_books(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category_id: Optional[int] = None,
    storage_type: Optional[StorageType] = None,
    search: Optional[str] = None
):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        query = supabase.table("books").select("""
            id, title, author, isbn, publisher, published_year, 
            language, cover_image, storage_type,
            categories(name),
            book_offline(quantity),
            book_online(access_url, platform_name)
        """)
        if category_id:
            query = query.eq("category_id", category_id)
        if storage_type:
            query = query.eq("storage_type", storage_type.value)
        if search:
            query = query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%")
        query = query.range(offset, offset + limit - 1)
        response = query.execute()
        books = []
        for book in response.data:
            books.append(BookResponse(
                id=book["id"],
                title=book["title"],
                author=book["author"],
                category_name=book["categories"]["name"] if book["categories"] else "Unknown",
                storage_type=book["storage_type"],
                isbn=book["isbn"],
                publisher=book["publisher"],
                published_year=book["published_year"],
                language=book["language"],
                cover_image=book["cover_image"],
                quantity=book["book_offline"]["quantity"] if book["book_offline"] else None,
                access_url=book["book_online"]["access_url"] if book["book_online"] else None,
                platform_name=book["book_online"]["platform_name"] if book["book_online"] else None
            ))
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        response = supabase.table("books").select("""
            id, title, author, isbn, publisher, published_year, 
            language, cover_image, storage_type,
            categories(name),
            book_offline(quantity),
            book_online(access_url, platform_name)
        """).eq("id", book_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Book not found")
        book = response.data[0]
        return BookResponse(
            id=book["id"],
            title=book["title"],
            author=book["author"],
            category_name=book["categories"]["name"] if book["categories"] else "Unknown",
            storage_type=book["storage_type"],
            isbn=book["isbn"],
            publisher=book["publisher"],
            published_year=book["published_year"],
            language=book["language"],
            cover_image=book["cover_image"],
            quantity=book["book_offline"][0]["quantity"] if book["book_offline"] else None,
            access_url=book["book_online"][0]["access_url"] if book["book_online"] else None,
            platform_name=book["book_online"][0]["platform_name"] if book["book_online"] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories():
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        categories_response = supabase.table("categories").select("*").execute()
        categories = []
        for category in categories_response.data:
            book_count_response = supabase.table("books").select("id").eq("category_id", category["id"]).execute()
            book_count = len(book_count_response.data)
            categories.append(CategoryResponse(
                id=category["id"],
                name=category["name"],
                description=category["description"],
                created_at=category["created_at"],
                book_count=book_count
            ))
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        response = supabase.table("categories").select("*").eq("id", category_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Category not found")
        category = response.data[0]
        book_count_response = supabase.table("books").select("id").eq("category_id", category_id).execute()
        book_count = len(book_count_response.data)
        return CategoryResponse(
            id=category["id"],
            name=category["name"],
            description=category["description"],
            created_at=category["created_at"],
            book_count=book_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/borrowers", response_model=List[BorrowerResponse])
async def get_borrowers(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_type: Optional[UserType] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None
):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        
        # Fetch borrow records with pagination
        borrow_query = supabase.table("borrow").select("*")
        if status:
            borrow_query = borrow_query.eq("status", status.value)
        borrow_query = borrow_query.range(offset, offset + limit - 1)
        borrow_response = borrow_query.execute()
        borrow_records = borrow_response.data

        if not borrow_records:
            print('No record Found')
            return []

        # Extract unique user_ids from borrow records
        user_ids = list({b["user_id"] for b in borrow_records})
        
        # Fetch corresponding user details
        users_query = supabase.table("users").select("""
            id, name, email, type, phone, status, last_login, joining_date,
            students(rollno, department, batch, semester),
            teachers(department, designation)
        """).in_("id", user_ids)

        if user_type:
            users_query = users_query.eq("type", user_type.value)
        if search:
            users_query = users_query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")

        users_response = users_query.execute()
        users_map = {u["id"]: u for u in users_response.data}

        borrowers = []

        for borrow in borrow_records:
            user = users_map.get(borrow["user_id"])
            if not user:
                continue  # Skip if user not found or filtered out

            borrower = BorrowerResponse(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                user_type=user["type"],
                phone=user["phone"],
                status=user["status"],
                last_login=user["last_login"],
                joining_date=user["joining_date"],
                books_borrowed=1  # Each record is one borrow
            )
            
            if user["type"] == "student" and user["students"]:
                student_data = user["students"]
                borrower.department = student_data["department"]
                borrower.rollno = student_data["rollno"]
                borrower.batch = student_data["batch"]
                borrower.semester = student_data["semester"]
            elif user["type"] == "teacher" and user["teachers"]:
                teacher_data = user["teachers"]
                borrower.department = teacher_data["department"]
                borrower.designation = teacher_data["designation"]

            borrowers.append(borrower)

        return borrowers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/borrowers/{borrower_id}", response_model=BorrowerResponse)
async def get_borrower(borrower_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # First, ensure this user has borrow records
        borrow_check = supabase.table("borrow").select("id").eq("user_id", borrower_id).execute()
        if not borrow_check.data:
            raise HTTPException(status_code=404, detail="No borrow records found for this user.")

        # Fetch the user details
        user_response = supabase.table("users").select("""
            id, name, email, type, phone, status, last_login, joining_date,
            students(rollno, department, batch, semester),
            teachers(department, designation)
        """).eq("id", borrower_id).execute()

        if not user_response.data:
            raise HTTPException(status_code=404, detail="Borrower not found")

        user = user_response.data[0]

        # Count approved borrows
        approved_borrows = supabase.table("borrow").select("id").eq("user_id", borrower_id).eq("status", "approved").execute()
        books_borrowed = len(approved_borrows.data)

        borrower = BorrowerResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            user_type=user["type"],
            phone=user["phone"],
            status=user["status"],
            last_login=user["last_login"],
            joining_date=user["joining_date"],
            books_borrowed=books_borrowed
        )

        if user["type"] == "student" and user.get("students"):
            student_data = user["students"]
            borrower.department = student_data["department"]
            borrower.rollno = student_data["rollno"]
            borrower.batch = student_data["batch"]
            borrower.semester = student_data["semester"]
        elif user["type"] == "teacher" and user.get("teachers"):
            teacher_data = user["teachers"]
            borrower.department = teacher_data["department"]
            borrower.designation = teacher_data["designation"]

        return borrower

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fines", response_model=List[FineResponse])
async def get_fines(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    paid: Optional[bool] = None,
    borrower_id: Optional[int] = None
):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        query = supabase.table("fines").select("""
            id, amount, paid, paid_date, payment_method, reason, created_at, borrow_id,
            borrow(
                users!borrow_user_id_fkey(name),
                books(title)
            )
        """)
        if paid is not None:
            query = query.eq("paid", paid)
        if borrower_id:
            query = query.eq("borrow.user_id", borrower_id)
        query = query.range(offset, offset + limit - 1)
        print('Hello')
        response = query.execute()
        print('Fines: ', response.data)
        if not response.data:
            return []
        
        fines = []
        for fine in response.data:
            borrower_name = fine["borrow"]["users"]["name"] if fine["borrow"] and fine["borrow"]["users"] else "Unknown"
            book_title = fine["borrow"]["books"]["title"] if fine["borrow"] and fine["borrow"]["books"] else "Unknown"
            fines.append(FineResponse(
                id=fine["id"],
                borrower_name=borrower_name,
                book_title=book_title,
                amount=fine["amount"],
                paid=fine["paid"],
                paid_date=fine["paid_date"],
                payment_method=fine["payment_method"],
                reason=fine["reason"],
                created_at=fine["created_at"],
                borrow_id=fine["borrow_id"]
            ))
        return fines
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fines/{fine_id}", response_model=FineResponse)
async def get_fine(fine_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        response = supabase.table("fines").select("""
            id, amount, paid, paid_date, payment_method, reason, created_at, borrow_id,
            borrow(
                users!borrow_user_id_fkey(name),
                books(title)
            )
        """).eq("id", fine_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Fine not found")
        fine = response.data[0]
        borrower_name = fine["borrow"]["users"]["name"] if fine["borrow"] and fine["borrow"]["users"] else "Unknown"
        book_title = fine["borrow"]["books"]["title"] if fine["borrow"] and fine["borrow"]["books"] else "Unknown"
        return FineResponse(
            id=fine["id"],
            borrower_name=borrower_name,
            book_title=book_title,
            amount=fine["amount"],
            paid=fine["paid"],
            paid_date=fine["paid_date"],
            payment_method=fine["payment_method"],
            reason=fine["reason"],
            created_at=fine["created_at"],
            borrow_id=fine["borrow_id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_all(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        books_response = supabase.table("books").select("""
            id, title, author, categories(name)
        """).or_(f"title.ilike.%{query}%,author.ilike.%{query}%").limit(limit).execute()
        categories_response = supabase.table("categories").select("""
            id, name, description
        """).or_(f"name.ilike.%{query}%,description.ilike.%{query}%").limit(limit).execute()
        borrowers_response = supabase.table("users").select("""
            id, name, email, type
        """).or_(f"name.ilike.%{query}%,email.ilike.%{query}%").limit(limit).execute()
        return {
            "books": books_response.data,
            "categories": categories_response.data,
            "borrowers": borrowers_response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def validate_book_input(data: dict):
    required_fields = ['title', 'author', 'publisher', 'published_year', 'language', 'category', 'storage_type']
    for field in required_fields:
        if not data.get(field):
            return f"Missing required book field: {field}"

    if data['storage_type'] not in ["online", "offline"]:
        return "Invalid storage type."

    if data['storage_type'] == "online":
        for field in ['online_address', 'platform_name', 'access_url', 'format']:
            if not data.get(field):
                return f"Missing online book detail: {field}"

    if data['storage_type'] == "offline":
        for field in ['quantity', 'offline_address', 'shelf_no', 'room']:
            if not data.get(field):
                return f"Missing offline book detail: {field}"

    return None

def insert_book(data: dict):
    catergory_name = str(data.get('category'))
    librarian_mail = str(data.get('added_by'))
    
    print('category:',catergory_name)
    print('librarian:',librarian_mail)

    book_data = {
        "title": data["title"],
        "author": data["author"],
        "publisher": data["publisher"],
        "published_year": data["published_year"],
        "language": data["language"],
        "isbn": data.get("isbn"),
        "cover_image": data.get("cover_image"),
        "category_id": catergory_name,
        "tags": data.get("tags"),
        "storage_type": data["storage_type"],
        "added_by": librarian_mail  
    }

    result = supabase.table("books").insert(book_data).execute()
    if not result.data or not result.data[0].get("id"):
        raise Exception("Failed to insert book.")
    return result.data[0]["id"]

def insert_storage_data(book_id: int, data: dict):
    if data["storage_type"] == "online":
        online_data = {
            "id": book_id,
            "address": data["online_address"],
            "platform_name": data["platform_name"],
            "access_url": data["access_url"],
            "format": data["format"]
        }
        supabase.table("book_online").insert(online_data).execute()
    else:
        offline_data = {
            "id": book_id,
            "quantity": data["quantity"],
            "address": data["offline_address"],
            "shelf_no": data["shelf_no"],
            "room": data["room"]
        }
        supabase.table("book_offline").insert(offline_data).execute()

@app.post("/addbook")
async def addbook(
    title: str = Form(...),
    author: str = Form(...),
    publisher: str = Form(...),
    published_year: int = Form(...),
    language: str = Form(...),
    isbn: Optional[str] = Form(None),
    cover_image: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    storage_type: str = Form(...),
    online_address: Optional[str] = Form(None),
    platform_name: Optional[str] = Form(None),
    access_url: Optional[str] = Form(None),
    format: Optional[str] = Form(None),
    quantity: Optional[int] = Form(0),
    offline_address: Optional[str] = Form(None),
    shelf_no: Optional[str] = Form(None),
    room: Optional[str] = Form(None),
    added_by: Optional[str] = Form(None)
):
    try:
        form_data = locals()  # turns all parameters into a dict

        # 1. Validate input
        validation_error = validate_book_input(form_data)
        if validation_error:
            return JSONResponse(status_code=400, content={"error": validation_error})
        
        print('No error')
        # 2. Insert book
        book_id = insert_book(form_data)

        # 3. Insert storage-specific data
        insert_storage_data(book_id, form_data)

        return JSONResponse(status_code=200, content={"message": "Book added successfully."})

    except Exception as e:
        print("Error adding book:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# @app.post("/addbook")
# async def addbook(
#     title: str = Form(...),
#     author: str = Form(...),
#     publisher: str = Form(...),
#     published_year: int = Form(...),
#     language: str = Form(...),
#     isbn: str = Form(None),
#     cover_image: str = Form(None),
#     category: str = Form(None),
#     tags: str = Form(None),
#     storage_type: str = Form(...),
#     online_address: str = Form(None),
#     platform_name: str = Form(None),
#     access_url: str = Form(None),
#     format: str = Form(None),
#     quantity: int = Form(0),
#     offline_address: str = Form(None),
#     shelf_no: str = Form(None),
#     room: str = Form(None),
#     added_by: str = Form(None)
# ):
#     try:
#         if not all([title, author, publisher, published_year, language, category, storage_type]):
#             return JSONResponse(status_code=400, content={"error": "Missing required book fields in books"})
#         if storage_type not in ["online", "offline"]:
#             return JSONResponse(status_code=400, content={"error": "Invalid storage type."})
#         if storage_type == "online":
#             if not all([online_address, platform_name, access_url, format]):
#                 return JSONResponse(status_code=400, content={"error": "Missing online book details."})
#         if storage_type == "offline":
#             if not all([quantity, offline_address, shelf_no, room]):
#                 return JSONResponse(status_code=400, content={"error": "Missing offline book details."})
#         book_data = {
#             "title": title,
#             "author": author,
#             "publisher": publisher,
#             "published_year": published_year,
#             "language": language,
#             "isbn": isbn,
#             "cover_image": cover_image,
#             "category_id": 1,
#             "tags": tags,
#             "storage_type": storage_type,
#             "added_by": 6
#         }
#         book_result = supabase.table("books").insert(book_data).execute()
#         if not book_result.data or not book_result.data[0].get("id"):
#             return JSONResponse(status_code=500, content={"error": "Failed to insert book."})
#         book_id = book_result.data[0]["id"]
#         if storage_type == "online":
#             online_data = {
#                 "id": book_id,
#                 "address": online_address,
#                 "platform_name": platform_name,
#                 "access_url": access_url,
#                 "format": format
#             }
#             supabase.table("book_online").insert(online_data).execute()
#         else:
#             offline_data = {
#                 "id": book_id,
#                 "quantity": quantity,
#                 "address": offline_address,
#                 "shelf_no": shelf_no,
#                 "room": room
#             }
#             supabase.table("book_offline").insert(offline_data).execute()
#         return JSONResponse(status_code=200, content={"message": "Book added successfully."})
#     except Exception as e:
#         print("Error adding book:", str(e))
#         return JSONResponse(status_code=400, content={"error": str(e)})
    
def update_book_and_storage(book_id: int, data: dict):
    book_data = {
        "title": data["title"],
        "author": data["author"],
        "publisher": data["publisher"],
        "published_year": data["published_year"],
        "language": data["language"],
        "isbn": data.get("isbn"),
        "cover_image": data.get("cover_image"),
        "tags": data.get("tags"),
        "storage_type": data["storage_type"],
        "added_by": 6
    }

    if data.get("category_id"):
        book_data["category_id"] = data["category_id"]

    supabase.table("books").update(book_data).eq("id", book_id).execute()

    if data["storage_type"] == "online":
        online_data = {
            "id": book_id,
            "address": data["online_address"],
            "platform_name": data["platform_name"],
            "access_url": data["access_url"],
            "format": data["format"]
        }
        supabase.table("book_online").upsert(online_data).execute()
    else:
        offline_data = {
            "id": book_id,
            "quantity": data["quantity"],
            "address": data["offline_address"],
            "shelf_no": data["shelf_no"],
            "room": data["room"]
        }
        supabase.table("book_offline").upsert(offline_data).execute()


@app.post("/updatebook/{book_id}")
async def updatebook(
    book_id: int = Path(...),
    category_name: Optional[str] = Query(None),
    title: str = Form(...),
    author: str = Form(...),
    publisher: str = Form(...),
    published_year: int = Form(...),
    language: str = Form(...),
    isbn: Optional[str] = Form(None),
    cover_image: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    storage_type: str = Form(...),
    online_address: Optional[str] = Form(None),
    platform_name: Optional[str] = Form(None),
    access_url: Optional[str] = Form(None),
    format: Optional[str] = Form(None),
    quantity: Optional[int] = Form(0),
    offline_address: Optional[str] = Form(None),
    shelf_no: Optional[str] = Form(None),
    room: Optional[str] = Form(None),
    added_by: Optional[str] = Form(None)
):
    try:
        form_data = locals()
        form_data["book_id"] = book_id

        if category_name:
            category_result = supabase.table("categories").select("id").eq("name", category_name).single().execute()
            if not category_result.data:
                return JSONResponse(status_code=400, content={"error": f"Category '{category_name}' not found."})
            form_data["category_id"] = category_result.data["id"]
        else:
            return JSONResponse(status_code=400, content={"error": "Missing category name in query parameters."})

        validation_error = validate_book_input(form_data)
        if validation_error:
            return JSONResponse(status_code=400, content={"error": validation_error})
 
        update_book_and_storage(book_id, form_data)

        return JSONResponse(status_code=200, content={"message": "Book updated successfully."})

    except Exception as e:
        print("Error updating book:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/categories/{category_name}")
async def get_categoryBy_name( category_name : str = Path (...) ):
    try:
        result = supabase.table("categories").select("*").eq('name', category_name).execute()
        return {"category": result.data}
    except Exception as e:
        print("Error fetching category  by name :", str(e))
        return JSONResponse(status_code=500, content={"error": "Failed to fetch category by name."})

@app.post("/updatecategory/{category_id}")   
async def update_category(
    category_id: int = Path(...),
    category_name: str = Form(...),
    category_description: str = Form(...)
):
    try:
        if not category_id or not category_name or not category_description:
            return JSONResponse(status_code=400, content={"error": "All fields are required."})
        result = supabase.table("categories").update({
            "name": category_name,
            "description": category_description
        }).eq("id", category_id).execute()
        if not result.data:
            return JSONResponse(status_code=500, content={"error": "Failed to update category."})
        return RedirectResponse(url="/home", status_code=302)
    except Exception as e:
        print("Error updating category:", str(e))
        return JSONResponse(status_code=400, content={"error": str(e)})

# --- Lending & Borrowing APIs ---
@app.get("/lending", response_class=HTMLResponse)
async def lending_page(request: Request):
    session = get_session_data(request)
    name = session.get('name') or "U"
    context = {"request": request, 'name': name, 'firstletter': name[0]}
    return templates.TemplateResponse("book/lending.html", context)

@app.get("/mybooks", response_class=HTMLResponse)
async def mybooks_page(request: Request):
    session = get_session_data(request)
    name = session.get('name') or "U"
    context = {"request": request, 'name': name, 'firstletter': name[0]}
    return templates.TemplateResponse("book/mybooks.html", context)

@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request):
    session = get_session_data(request)
    name = session.get('name') or "U"
    context = {"request": request, 'name': name, 'firstletter': name[0]}
    return templates.TemplateResponse("notification.html", context)

@app.post("/api/borrow/request")
async def request_borrow(request: Request, data: Optional[dict] = None):
    data = await request.json()
    session = get_session_data(request)
    user_id = session.get('id')
    if not user_id:
        return {"success": False, "error": "Not logged in."}
    if not data:
        return {'success': False, 'error': data}
    book_id = data.get('book_id')
    request_description = data.get('request_description', '').strip()
    return_date = data.get('return_date', '').strip()
    if not book_id:
        return {"success": False, "error": "Book ID required."}
    if not request_description:
        return {"success": False, "error": "Request description is required."}
    if not return_date:
        return {"success": False, "error": "Return date is required."}
    try:
        # Validate return_date format (YYYY-MM-DD)
        _ = datetime.strptime(return_date, "%Y-%m-%d")
    except Exception:
        return {"success": False, "error": "Invalid return date format. Use YYYY-MM-DD."}
    # Check if already borrowed or pending
    existing = supabase.table("borrow").select("*").eq("user_id", user_id).eq("book_id", book_id).in_("status", ["pending", "approved"]).execute()
    if existing.data:
        return {"success": False, "error": "You already have a pending or approved request for this book."}
    # Insert borrow request
    result = supabase.table("borrow").insert({
        "user_id": user_id,
        "book_id": book_id,
        "request_description": request_description,
        "request_date": datetime.now().isoformat(),
        "return_date": return_date,
        "approved_by": None, # librarian
        "approved_date": None,
        "return_condition": None,
    }).execute()
    # Create notification for librarian(s)
    book = supabase.table("books").select("title,author").eq("id", book_id).single().execute().data
    user = supabase.table("users").select("name,email").eq("id", user_id).single().execute().data
    notif_msg = f"{user['name']} requested to borrow '{book['title']}' by {book['author']}"
    supabase.table("notifications").insert({
        "user_id": user_id,
        "type": "borrow_request",
        "message": notif_msg,
        "book_id": book_id,
        "created_at": datetime.now().isoformat()
    }).execute()
    return {"success": True}

@app.get("/api/mybooks")
async def api_mybooks(request: Request):
    session = get_session_data(request)
    user_id = session.get('id')
    if not user_id:
        return []
    borrows = supabase.table("borrow").select("*", "books(*)").eq("user_id", user_id).order("request_date", desc=True).execute().data
    result = []
    for b in borrows:
        book = b.get('books', {})
        # Get category name if possible
        category_name = ""
        if book.get('category_id'):
            cat_resp = supabase.table("categories").select("name").eq("id", book['category_id']).single().execute().data
            if cat_resp:
                category_name = cat_resp.get('name', '')
        # Get librarian name if approved
        librarian_name = ""
        if b.get('status') == 'approved' and b.get('approved_by'):
            librarian = supabase.table("users").select("name").eq("id", b['approved_by']).single().execute().data
            if librarian:
                librarian_name = librarian.get('name', '')
        # Format request date
        request_time = ""
        if b.get('request_date'):
            try:
                dt = datetime.fromisoformat(b['request_date'].replace('Z',''))
                request_time = dt.strftime("%b %d, %Y")
            except Exception:
                request_time = b['request_date']
        result.append({
            "title": book.get('title'),
            "author": book.get('author'),
            "category_name": category_name,
            "status": b.get('status', 'pending'),
            "request_time": request_time,
            "librarian_name": librarian_name,
            "isbn": book.get('isbn'),
            "publisher": book.get('publisher'),
            "published_year": book.get('published_year'),
            "language": book.get('language'),
            "cover_image": book.get('cover_image'),
        })
    return result

@app.get("/api/notifications")
async def api_notifications(request: Request):
    session = get_session_data(request)
    user_id = session.get('id')
    user_type = session.get('type')
    if user_type == 'librarian':
        notifs = supabase.table("notifications").select("*").eq("type", "borrow_request").order("created_at", desc=True).execute().data
    else:
        notifs = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data

    # Enrich notifications with user name and book title
    for n in notifs:
        # Add action/title for librarian
        if user_type == 'librarian' and n['type'] == 'borrow_request' and n.get('status') != 'approved':
            n['action'] = 'Approve'
            n['title'] = 'Borrow Request'
        else:
            n['action'] = ''
            n['title'] = 'Notification'

        # Add user_name
        user_name = ''
        if n.get('user_id'):
            user = supabase.table('users').select('name').eq('id', n['user_id']).single().execute().data
            if user:
                user_name = user.get('name', '')
        n['user_name'] = user_name

        # Add book_title
        book_title = ''
        if n.get('book_id'):
            book = supabase.table('books').select('title').eq('id', n['book_id']).single().execute().data
            if book:
                book_title = book.get('title', '')
        n['book_title'] = book_title

    return notifs

@app.post("/api/notifications/{notif_id}/approve")
async def approve_borrow_request(request: Request, notif_id: int = Path(...)):
    try:
        session = get_session_data(request)
        librarian_id = session.get('id')
        
        if not librarian_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Not authenticated."})
        
        # Check if user is a librarian
        user_type = session.get('type')
        if user_type != 'librarian':
            return JSONResponse(status_code=403, content={"success": False, "error": "Only librarians can approve borrow requests."})
        
        print('notification Id: ', notif_id)
        
        # Fetch the notification
        notif_resp = supabase.table("notifications").select("*").eq("id", notif_id).execute()
        
        if not notif_resp.data:
            return JSONResponse(status_code=404, content={"success": False, "error": "Notification not found."})
        
        notif = notif_resp.data[0]
        print('Notification data:', notif)
        
        # Check if notification is a borrow request and still pending
        if notif.get('type') != 'borrow_request':
            return JSONResponse(status_code=400, content={"success": False, "error": "This is not a borrow request notification."})
        
        if notif.get('status') == 'approved':
            return JSONResponse(status_code=400, content={"success": False, "error": "This request has already been approved."})
        
        # Find the related borrow request
        borrow_resp = supabase.table("borrow").select("*").eq("user_id", notif['user_id']).eq("book_id", notif['book_id']).eq("status", "pending").execute()
        
        if not borrow_resp.data:
            return JSONResponse(status_code=404, content={"success": False, "error": "Borrow request not found or already processed."})
        
        borrow = borrow_resp.data[0]
        print('Borrow data:', borrow)
        
        # Approve borrow request
        supabase.table("borrow").update({
            "status": "approved",
            "approved_by": librarian_id,
            "approved_date": datetime.now().isoformat()
        }).eq("id", borrow['id']).execute()
        
        # Update notification status
        supabase.table("notifications").update({"status": "approved"}).eq("id", notif_id).execute()
        
        return JSONResponse(status_code=200, content={"success": True, "message": "Borrow request approved successfully."})
        
    except Exception as e:
        print("Error in approve_borrow_request:", str(e))
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})



# --- Helper Functions ---
def get_category_id(category_name: str) -> int:
    """
    Fetch the category_id from the categories table given a category name.
    Raises an Exception if not found.
    """
    if not category_name:
        raise Exception("Category name is required.")
    result = supabase.table("categories").select("id").eq("name", category_name).single().execute()
    if not result.data or not result.data.get("id"):
        raise Exception(f"Category '{category_name}' not found.")
    return result.data["id"]

def get_librarian_id(librarian_mail: str) -> int:
    """
    Fetch the librarian_id (added_by) for the book. This can be customized as needed.
    For now, returns the first librarian's id. Optionally, you can use session data.
    """
    result = supabase.table("users").select("id").eq("type", "librarian").eq("status", "active").eq('email',librarian_mail).limit(1).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]["id"]
    raise Exception("No active librarian found to assign as 'added_by'.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)