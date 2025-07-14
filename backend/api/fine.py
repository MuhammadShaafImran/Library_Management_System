from models.borrow import FineResponse
from fastapi import APIRouter, HTTPException, Query
from core.supabase_client import get_supabase_client
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import Optional, List
from models.borrow import FineResponse


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/api/fines", response_model=List[FineResponse])
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

@router.get("/api/fines/{fine_id}", response_model=FineResponse)
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

@router.delete("/api/fines/{fine_id}/delete")
async def delete_fine(fine_id: int):
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        result = supabase.table("fines").delete().eq("id", fine_id).execute()
        if not result.data:
            return JSONResponse(status_code=404, content={"success": False, "error": "Fine not found or could not be deleted."})
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})