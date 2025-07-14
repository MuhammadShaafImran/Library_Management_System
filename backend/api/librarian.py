from fastapi import APIRouter, HTTPException
from core.supabase_client import get_supabase_client
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import List
from schemas.lending import BorrowerResponse
from schemas.user import LibrarianResponse
from datetime import datetime


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/api/librarians/active", response_model=List[BorrowerResponse])
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
    
@router.get("/api/librarians", response_model=List[LibrarianResponse])
async def get_librarians():
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        response = supabase.table("users").select("*, librarians(admin)").eq("type", "librarian").execute()

        if not response:
            raise Exception(response.error)

        data = response.data or []
        librarians = []


        for user in data:
            librarian_info = user.get("librarians", {})
            librarians.append(LibrarianResponse(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                phone=user.get("phone"),
                status=user["status"],
                last_login= convert_date_format(user.get("last_login")),
                joining_date= convert_date_format(user.get("joining_date")),
                admin=librarian_info.get("admin")
            ))

        return librarians

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching librarians: {str(e)}")
    

def convert_date_format(Date: str| None) -> str:
    if Date:
        dt = datetime.fromisoformat(Date)
        converted_Date = dt.strftime("%b %d, %Y")
        return converted_Date
    else:
        return ""

