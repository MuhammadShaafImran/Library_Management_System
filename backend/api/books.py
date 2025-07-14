from services.book import validate_book_input, insert_book, insert_storage_data
from fastapi import APIRouter, HTTPException, Query, Form, Request, Path
from core.supabase_client import get_supabase_client
from core.user import get_session_data
from schemas.book import BookResponse, StorageType
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from schemas.book import BookResponse, DashboardStats
from typing import Optional, List
from datetime import datetime, timedelta
from services.book import update_book_and_storage
from services.category import get_category_id
from datetime import date


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/addbook")
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
        form_data = locals()
        form_data['category_id'] = int(form_data['category'])
        validation_error = validate_book_input(form_data)
        if validation_error:
            return JSONResponse(status_code=400, content={"error": validation_error})
        print('No error')
        book_id = insert_book(form_data)
        insert_storage_data(book_id, form_data)
        return JSONResponse(status_code=200, content={"message": "Book added successfully."})

    except Exception as e:
        print("Error adding book:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.delete("/api/books/{book_id}/delete")
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
    
@router.get("/api/books", response_model=List[BookResponse])
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
            language, cover_image, rating, storage_type,
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
                category=book["categories"]["name"] if book["categories"] else "Unknown",
                storage_type=book["storage_type"],
                isbn=book["isbn"],
                publisher=book["publisher"],
                published_year=book["published_year"],
                language=book["language"],
                cover_image=book["cover_image"],
                rating=book["rating"],
                quantity=book["book_offline"]["quantity"] if book["book_offline"] else None,
                access_url=book["book_online"]["access_url"] if book["book_online"] else None,
                platform_name=book["book_online"]["platform_name"] if book["book_online"] else None
            ))
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        response = supabase.table("books").select("""
            id, title, author, isbn, publisher, published_year, 
            language, cover_image, rating,storage_type,
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
            category=book["categories"]["name"] if book["categories"] else "Unknown",
            storage_type=book["storage_type"],
            isbn=book["isbn"],
            publisher=book["publisher"],
            published_year=book["published_year"],
            language=book["language"],
            cover_image=book["cover_image"],
            rating=book["rating"],
            quantity=book["book_offline"]["quantity"] if book["book_offline"] else None,
            access_url=book["book_online"]["access_url"] if book["book_online"] else None,
            platform_name=book["book_online"]["platform_name"] if book["book_online"] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/updatebook/{book_id}")
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
        
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Subabase Client not defined."})

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

@router.get("/api/mybooks")
async def api_mybooks(request: Request):
    session = get_session_data(request)
    supabase = get_supabase_client()
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Subabase Client not defined."})

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
        librarian = supabase.table("users").select("name").eq("id", b['approved_by']).single().execute().data
        if librarian:
            librarian_name = librarian.get('name', '')
        # Format request date
        return_time = ""
        if b.get('return_date'):
            try:
                dt = datetime.fromisoformat(b['return_date'].replace('Z',''))
                return_time = dt.strftime("%b %d, %Y")
            except Exception:
                return_time = b['return_date']
                
        result.append({
            "title": book.get('title'),
            "author": book.get('author'),
            "category_name": category_name,
            "status": b.get('status', 'pending'),
            "return_date": return_time,
            "librarian_name": librarian_name,
            "isbn": book.get('isbn'),
            "publisher": book.get('publisher'),
            "published_year": book.get('published_year'),
            "language": book.get('language'),
            "cover_image": book.get('cover_image'),
        })
    return result

@router.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # Current month
        books_response = supabase.table("books").select("id, created_at").execute()
        total_books = len(books_response.data)
        # print('Books', books_response, "total books", total_books)
        categories_response = supabase.table("categories").select("id,created_at").execute()
        total_categories = len(categories_response.data)
        # print('categories',categories_response, "total categories", total_categories)
        active_borrowers_response = supabase.table("borrow").select("user_id, request_date,status").eq("status", "approved").execute()
        active_borrowers = len(set([b["user_id"] for b in active_borrowers_response.data]))
        # print('active_borrowers_resp', active_borrowers, "active_borrowers", active_borrowers)
        pending_fines_response = supabase.table("fines").select("amount,created_at,paid").eq("paid", False).execute()
        pending_fines = sum(fine["amount"] for fine in pending_fines_response.data)
        # print('pending_fines :', pending_fines,' resp: ',pending_fines_response)
        today = datetime.now()
        first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 12:
            first_of_next_month = today.replace(year=today.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            first_of_next_month = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_of_this_month = first_of_next_month - timedelta(seconds=1)
        # Books last month
        total_books_last_month = len([
            b for b in books_response.data
            if b.get("created_at") and first_of_this_month <= datetime.fromisoformat(b["created_at"].replace('Z','')) <= last_of_this_month
        ])
        # Categories last month
        total_categories_last_month = len([
            c for c in categories_response.data
            if c.get("created_at") and first_of_this_month <= datetime.fromisoformat(c["created_at"].replace('Z','')) <= last_of_this_month
        ])
        # Active borrowers last month
        active_borrowers_last_month = len(set([
            b["user_id"] for b in active_borrowers_response.data
            if b.get("borrowed_at") and first_of_this_month <= datetime.fromisoformat(b["borrowed_at"].replace('Z','')) <= last_of_this_month
        ]))
        # Pending fines last month
        pending_fines_last_month = sum([
            f["amount"] for f in pending_fines_response.data
            if f.get("created_at") and first_of_this_month <= datetime.fromisoformat(f["created_at"].replace('Z','')) <= last_of_this_month
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

@router.get("/api/search")
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

@router.get("/api/books/{book_id}/offline_address")
async def get_offline_book_address(book_id: int):
    supabase = get_supabase_client()
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
    resp = supabase.table("book_offline").select("address, shelf_no, room").eq("id", book_id).single().execute()
    if not resp.data:
        return JSONResponse(status_code=404, content={"error": "Offline book address not found."})
    return {
        "address": resp.data.get("address"),
        "shelf_no": resp.data.get("shelf_no"),
        "room": resp.data.get("room")
    }