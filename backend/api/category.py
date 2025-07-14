# DELETE category endpoint
from fastapi import status
from fastapi import APIRouter, HTTPException, Query, Form, Request, Path
from core.supabase_client import get_supabase_client
from core.user import get_session_data
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
from datetime import datetime
from models.book import CategoryResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/addcategory")
async def add_category(
    category_name: str = Form(...),
    category_description: str = Form(...)
):
    try:
        supabase = get_supabase_client()
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
    
@router.get("/api/categories", response_model=List[CategoryResponse])
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

@router.get("/api/categories/{category_id}", response_model=CategoryResponse)
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

@router.get("/categories/{category_name}")
async def get_categoryBy_name( category_name : str = Path (...) ):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        result = supabase.table("categories").select("*").eq('name', category_name).execute()
        return {"category": result.data}
    except Exception as e:
        print("Error fetching category  by name :", str(e))
        return JSONResponse(status_code=500, content={"error": "Failed to fetch category by name."})

@router.post("/updatecategory/{category_id}")   
async def update_category(
    category_id: int = Path(...),
    category_name: str = Form(...),
    category_description: str = Form(...)
):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
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

@router.delete("/api/categories/{category_id}/delete")
async def delete_category(category_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        # Optionally, delete all books in this category first (if ON DELETE CASCADE is not set)
        supabase.table("books").delete().eq("category_id", category_id).execute()
        result = supabase.table("categories").delete().eq("id", category_id).execute()
        if not result.data:
            return JSONResponse(status_code=404, content={"success": False, "error": "Category not found or could not be deleted."})
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})