from fastapi import FastAPI, Request, Query, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
import os


app = FastAPI()


# Set up templates and static files directory
app.mount("/static", StaticFiles(directory="../frontend/static/"), name="static")
templates = Jinja2Templates(directory="../frontend/templates/")

load_dotenv(dotenv_path='../.env.local')

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get('/register',response_class=HTMLResponse)
def register(request:Request):
    return templates.TemplateResponse("auth/signUp.html", {"request": request})

@app.get('/login',response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("auth/signIn.html", {"request": request})

@app.post("/addcategory")
async def add_category(
    category_name: str = Form(...),
    category_description: str = Form(...)
):
    try:
        if not category_name or not category_description:
            return JSONResponse(status_code=400, content={"error": "Category name and description are required."})
        today = datetime.now().date().isoformat()
        # Insert into categories table
        result = supabase.table("categories").insert({
            "name": category_name,
            "description": category_description,
            "created_at": today
        }).execute()
        if not result.data:
            return JSONResponse(status_code=500, content={"error": "Failed to add category."})
        # Optionally, redirect or return success
        return RedirectResponse(url="/add-book", status_code=302)
    except Exception as e:
        print("Error adding category:", str(e))
        return JSONResponse(status_code=400, content={"error": str(e)})
    

# Category page route
@app.get('/add-category', response_class=HTMLResponse)
async def add_category_page(request: Request):
    return templates.TemplateResponse("book/category.html", {"request": request})

# Routes for book management
@app.get('/add-book',response_class=HTMLResponse)
async def add_book_page(request: Request):
    return templates.TemplateResponse("book/add_books.html", {"request": request})

@app.get('/home')
def loadhomePage(request:Request):
    return templates.TemplateResponse("home/home.html", {"request": request})


# Add Book API (from form)
@app.post("/addbook")
async def addbook(
    # Book base fields
    title: str = Form(...),
    author: str = Form(...),
    publisher: str = Form(...),
    published_year: int = Form(...),
    language: str = Form(...),
    isbn: str = Form(None),
    cover_image: str = Form(None),
    category: str = Form(None),
    tags: str = Form(None),
    storage_type: str = Form(...),
    # Online fields
    online_address: str = Form(None),
    platform_name: str = Form(None),
    access_url: str = Form(None),
    format: str = Form(None),
    # Offline fields
    quantity: int = Form(0),
    offline_address: str = Form(None),
    shelf_no: str = Form(None),
    room: str = Form(None),
    # User info (for added_by)
    added_by: str = Form(None)
):
    try:
        # Validate required fields
        print(title, " ", author, " ", publisher,  " ", published_year,  " ", language,  " ", category,  " ", storage_type)

        if not all([title, author, publisher, published_year, language, category, storage_type]):
            return JSONResponse(status_code=400, content={"error": "Missing required book fields in books"})
        if storage_type not in ["online", "offline"]:
            return JSONResponse(status_code=400, content={"error": "Invalid storage type."})

        # Validate online/offline fields
        if storage_type == "online":
            if not all([online_address, platform_name, access_url, format]):
                return JSONResponse(status_code=400, content={"error": "Missing online book details in online =."})
        if storage_type == "offline":
            if not all([quantity, offline_address, shelf_no, room]):
                return JSONResponse(status_code=400, content={"error": "Missing offline book details."})


        # Insert into books table
        book_data = {
            "title": title,
            "author": author,
            "publisher": publisher,
            "published_year": published_year,
            "language": language,
            "isbn": isbn,
            "cover_image": cover_image,
            "category_id": 1,
            "tags": tags,
            "storage_type": storage_type,
            "added_by": 6
        }
        book_result = supabase.table("books").insert(book_data).execute()
        if not book_result.data or not book_result.data[0].get("id"):
            return JSONResponse(status_code=500, content={"error": "Failed to insert book."})
        book_id = book_result.data[0]["id"]

        # Insert into online/offline table
        if storage_type == "online":
            online_data = {
                "id": book_id,
                "address": online_address,
                "platform_name": platform_name,
                "access_url": access_url,
                "format": format
            }
            supabase.table("book_online").insert(online_data).execute()
        else:
            offline_data = {
                "id": book_id,
                "quantity": quantity,
                "address": offline_address,
                "shelf_no": shelf_no,
                "room": room
            }
            supabase.table("book_offline").insert(offline_data).execute()

        return JSONResponse(status_code=200, content={"message": "Book added successfully."})
    except Exception as e:
        print("Error adding book:", str(e))
        return JSONResponse(status_code=400, content={"error": str(e)})
# Routes for borrowing and returning books
@app.post("/borrow")
def borrow_book(borrow_info: dict):
    return {"message": "Book borrowed successfully", "borrow_info": borrow_info}

@app.post("/return")
def return_book(return_info: dict):
    return {"message": "Book returned successfully", "return_info": return_info}


@app.post('/login')
def login_user(email: str = Form(...), password: str = Form(...)):
    # email = user.get('email')
    # password = user.get('password')

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    print('Inside login_user:',email," ",password)
    try:
        # Verify credentials
        user_data = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
        if not user_data.data:
            return {"error": "Invalid email or password"}, 401

        # Update last login timestamp
        supabase.table('users').update({"last_login": datetime.now().isoformat()}).eq('email', email).execute()

        # return {"message": "Login successful", "data": user_data.data}, 200
        
        return RedirectResponse(url="/home", status_code=302)
        # return templates.TemplateResponse("home/index.html", {"request": request})
    except Exception as e:
        return {"error": str(e)}, 400

@app.post("/registerForm")
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    type: str = Form(...),
    phone: str | None = Form(None),

    # Student-specific
    roll_no: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    batch: Optional[str] = Form(None),
    semester: Optional[str] = Form(None),

    # Teacher-specific
    teacher_department: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),

    # Librarian-specific
    admin: Optional[bool] = Form(False),
):
    try:
        # Basic validation
        if not name or not email or not password:
            return JSONResponse(status_code=400, content={"error": "Name, email, and password are required"})

        # Check if email exists
        existing_user = supabase.table('users').select('email').eq('email', email).execute()
        if existing_user.data:
            return JSONResponse(status_code=400, content={"error": "Email already exists"})

        today = datetime.now().isoformat()

        # Insert base user
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



@app.get("/api/books")
def get_books(
    genre: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("title")
):
    try:
        query = supabase.table("books").select("*")

        # Apply filters
        if genre:
            query = query.eq("genre", genre)
        if status:
            query = query.eq("status", status)
        if year:
            query = query.eq("published_year", year)

        # Fetch data
        books = query.execute().data

        # Apply sorting
        if sort_by == "title":
            books.sort(key=lambda x: x["title"])
        elif sort_by == "author":
            books.sort(key=lambda x: x["author"])
        elif sort_by == "year":
            books.sort(key=lambda x: x["published_year"], reverse=True)

        return {"books": books}
    except Exception as e:
        return {"error": str(e)}, 500