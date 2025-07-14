from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.user import get_user_name, get_session_data
from typing import Optional
from services.book import get_book_by_id
from services.category import get_category_by_id, get_books_by_category

from api.books import router as book_router
from api.borrow import router as borrow_router
from api.category import router as cat_router
from api.fine import router as fine_router
from api.librarian import router as lib_router
from api.notifications import router as noti_router
# from api.record import router as record_router
from api.user import router as user_router


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

app.include_router(borrow_router)
app.include_router(book_router)
app.include_router(cat_router)
app.include_router(fine_router)
app.include_router(lib_router)
app.include_router(noti_router)
app.include_router(user_router)


# --- public Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    context = get_user_name(request)
    if context['name'] == "Unknown":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("home/home.html", context)

@app.get('/register', response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@app.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

# --- User Endpoints ---
@app.get('/managers',response_class=HTMLResponse)
def managers(request:Request):
    context = get_user_name(request)
    if context['name'] == "Unknown":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse('user/managers.html',context)

@app.get('/profile', response_class=HTMLResponse)
def profile(request:Request):
    context = get_user_name(request)
    if context['name'] == "Unknown":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("user/profile.html", context)

@app.get("/mybooks", response_class=HTMLResponse)
async def mybooks_page(request: Request):
    context = get_user_name(request)
    if context['name'] == "Unknown":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("book/mybooks.html", context)

@app.get('/book/{book_id}', response_class=HTMLResponse)
async def book_detail_page(request: Request, book_id: int):
    context = get_user_name(request)
    if context['name'] == "Unknown":
        return RedirectResponse(url="/login")
    
    book = await get_book_by_id(book_id)
    if not book:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Book not found."})
    context['book'] = book
    # Fetch related books from the same category (excluding this book)
    related_books = []
    if book.get('category'):
        related_books = await get_books_by_category(book['category'], exclude_id=book_id, limit=5)
    context['related_books'] = related_books
    return templates.TemplateResponse("book/book.html", context)

@app.get("/lending", response_class=HTMLResponse)
async def lending_page(request: Request):
    context = get_user_name(request)
    return templates.TemplateResponse("book/lending.html", context)

# --- Admin Endpoints ---
@app.get('/add-book', response_class=HTMLResponse)
async def add_book_page(request: Request, book_id: Optional[int] = Query(None)):
    if verify_admin(request):
        context = get_user_name(request)
        if context['name'] == "Unknown":
            return RedirectResponse(url="/login")
        if book_id:
            book = await get_book_by_id(book_id)
            if book is not None:
                context['book'] = book
            else:
                context['book'] = {}
        else:
            context['book'] = {}
        return templates.TemplateResponse("book/add_books.html", context)
    return RedirectResponse(url="/")

@app.get('/add-category', response_class=HTMLResponse)
async def add_category_page(request: Request, category_id: Optional[int] = Query(None)):
    if verify_admin(request):
        context = get_user_name(request)
        if category_id:
            category = get_category_by_id(category_id)
            if category:
                    context['category'] = category
            else:
                context['category'] = {}
        else:
            context['category'] = {}
        return templates.TemplateResponse("book/category.html", context)
    
    return RedirectResponse(url="/")

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request):
    if verify_admin(request):
        context = get_user_name(request)
        return templates.TemplateResponse("dashboard/dashboard.html", context)
    return RedirectResponse(url='/')

@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request):
    if verify_admin(request):
        context = get_user_name(request)
        return templates.TemplateResponse("user/notification.html", context)
    return RedirectResponse(url='/mybooks')

@app.get('/test', response_class=HTMLResponse)
def test(request: Request):
    return templates.TemplateResponse("/book/book.html", {"request": request})

def verify_admin(request:Request):
    session = get_session_data(request)
    if session:
        return session['type'] == "librarian"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)