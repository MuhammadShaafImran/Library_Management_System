from models.borrow import FineResponse
from fastapi import APIRouter, HTTPException, Query, Body
from core.supabase_client import get_supabase_client
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import Optional, List
from models.borrow import FineResponse
from datetime import datetime, timedelta


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
        response = query.execute()
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
    

# Calculate fine amount based on due and return dates
def calculate_fine_amount(return_date: str, current_date: Optional[str] = None) -> int:
    """Calculate fine amount based on due date and current/return date."""
    if current_date is None:
        current_date = datetime.now().date().isoformat()
    
    due = datetime.strptime(return_date, "%Y-%m-%d").date()
    current = datetime.strptime(current_date, "%Y-%m-%d").date()
    
    days_late = (current - due).days
    print('days_late:', days_late)
    return max(0, days_late * 100)

# Helper function to get due date (typically 14 days from approval date)
def calculate_due_date(approval_date: str, loan_period_days: int = 14) -> str:
    """Calculate due date based on approval date and loan period."""
    approval = datetime.strptime(approval_date, "%Y-%m-%d")
    return_date = approval + timedelta(days=loan_period_days)
    return return_date.date().isoformat()

@router.post("/api/fines/create-on-approval")
async def create_fine_on_approval(borrow_id: int, user_id: int, approval_date: str):
    """
    Create initial fine record when a borrow request is approved.
    Called from the approval endpoint.
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # Calculate due date (14 days from approval)
        return_date = calculate_due_date(approval_date)
        
        # Create initial fine record with 0 amount
        fine_data = {
            "borrow_id": borrow_id,
            "user_id": user_id,
            "amount": 0,  # Initial amount is 0
            "paid": False,
            "reason": "Initial fine record - no fine yet",
            "created_at": datetime.now().date().isoformat()
        }
        
        # Insert fine record
        fine_resp = supabase.table("fines").insert(fine_data).execute()
        
        # Update borrow record with due date
        supabase.table("borrow").update({
            "return_date": return_date
        }).eq("id", borrow_id).execute()
        
        return {"success": True, "return_date": return_date, "fine_id": fine_resp.data[0]["id"] if fine_resp.data else None}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/fines/update-overdue")
async def update_overdue_fines(user_id: Optional[int] = None):
    """
    Update all overdue fines. Can be called for a specific user or all users.
    Called on user login and borrow requests.
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        print('Updating Fine Working')
        # Get all approved borrow records that haven't been returned
        query = supabase.table("borrow").select("""
            id, user_id, book_id, return_date, return_date, status
        """).eq("status", "approved")
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        borrow_response = query.execute()
        if not borrow_response.data:
            return {"success": True, "message": "No active borrows found."}
        
        print('borrow_reponse: ', borrow_response)

        updated_fines = []
        current_date = datetime.now().date().isoformat()
        
        for borrow in borrow_response.data:
            if borrow["return_date"]:
                # Calculate current fine amount
                fine_amount = calculate_fine_amount(borrow["return_date"], current_date)
                
                # Update or create fine record
                existing_fine = supabase.table("fines").select("*").eq("borrow_id", borrow["id"]).execute()
                
                if existing_fine.data:
                    # Update existing fine
                    fine_id = existing_fine.data[0]["id"]
                    if existing_fine.data[0]["amount"] != fine_amount:
                        supabase.table("fines").update({
                            "amount": fine_amount,
                            "reason": f"Overdue fine - {(datetime.strptime(current_date, '%Y-%m-%d').date() - datetime.strptime(borrow['return_date'], '%Y-%m-%d').date()).days} days late" if fine_amount > 0 else "No fine - returned on time"
                        }).eq("id", fine_id).execute()
                        updated_fines.append({"borrow_id": borrow["id"], "fine_amount": fine_amount})
                else:
                    # Create fine record if it doesn't exist
                    fine_data = {
                        "borrow_id": borrow["id"],
                        "user_id": borrow["user_id"],
                        "amount": fine_amount,
                        "paid": False,
                        "reason": f"Overdue fine - {(datetime.strptime(current_date, '%Y-%m-%d').date() - datetime.strptime(borrow['return_date'], '%Y-%m-%d').date()).days} days late" if fine_amount > 0 else "No fine",
                        "created_at": current_date
                    }
                    supabase.table("fines").insert(fine_data).execute()
                    updated_fines.append({"borrow_id": borrow["id"], "fine_amount": fine_amount})
        
        print('Fine updated: ', updated_fines)
        
        return {"success": True, "updated_fines": updated_fines}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/fines/user/{user_id}/total")
async def get_user_total_fines(user_id: int):
    """Get total unpaid fines for a user."""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # First update overdue fines for this user
        await update_overdue_fines(user_id)
        
        # Get all unpaid fines for the user
        fines_response = supabase.table("fines").select("amount").eq("user_id", user_id).eq("paid", False).execute()
        
        total_fine = sum(fine["amount"] for fine in fines_response.data) if fines_response.data else 0
        
        return {"success": True, "user_id": user_id, "total_unpaid_fines": total_fine}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/fines/{fine_id}/pay")
async def pay_fine(fine_id: int, payment_method: str = Body(..., embed=True)):
    """Mark a fine as paid."""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # Update fine as paid
        result = supabase.table("fines").update({
            "paid": True,
            "paid_date": datetime.now().date().isoformat(),
            "payment_method": payment_method
        }).eq("id", fine_id).execute()
        
        if not result.data:
            return JSONResponse(status_code=404, content={"success": False, "error": "Fine not found."})
        
        return {"success": True, "message": "Fine paid successfully."}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/fines/finalize-on-return")
async def finalize_fine_on_return(borrow_id: int, return_date: str):
    """
    Finalize fine when a book is returned.
    Calculate final fine amount based on actual return date.
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # Get borrow record
        borrow_resp = supabase.table("borrow").select("id, user_id, return_date").eq("id", borrow_id).single().execute()
        if not borrow_resp.data:
            return JSONResponse(status_code=404, content={"error": "Borrow record not found."})

        borrow = borrow_resp.data
        return_date = borrow.get("return_date") or ""
        
        if not return_date:
            return JSONResponse(status_code=400, content={"error": "Due date not found for this borrow record."})

        # Calculate final fine amount
        final_fine_amount = calculate_fine_amount(return_date, return_date)
        
        # Update fine record
        fine_resp = supabase.table("fines").select("id").eq("borrow_id", borrow_id).execute()
        
        if fine_resp.data:
            fine_id = fine_resp.data[0]["id"]
            supabase.table("fines").update({
                "amount": final_fine_amount,
                "reason": f"Final fine - returned on {return_date}. " + 
                         (f"{(datetime.strptime(return_date, '%Y-%m-%d').date() - datetime.strptime(return_date, '%Y-%m-%d').date()).days} days late" if final_fine_amount > 0 else "Returned on time")
            }).eq("id", fine_id).execute()
        else:
            # Create fine record if it doesn't exist
            fine_data = {
                "borrow_id": borrow_id,
                "user_id": borrow["user_id"],
                "amount": final_fine_amount,
                "paid": False,
                "reason": f"Final fine - returned on {return_date}. " + 
                         (f"{(datetime.strptime(return_date, '%Y-%m-%d').date() - datetime.strptime(return_date, '%Y-%m-%d').date()).days} days late" if final_fine_amount > 0 else "Returned on time"),
                "created_at": datetime.now().date().isoformat()
            }
            supabase.table("fines").insert(fine_data).execute()

        # Update borrow record with return date
        supabase.table("borrow").update({
            "return_date": return_date,
            "status": "returned"  # Add this status if not exists in your enum
        }).eq("id", borrow_id).execute()

        return {"success": True, "final_fine_amount": final_fine_amount}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/fines/daily-update")
async def daily_fine_update():
    """
    Daily task to update all overdue fines.
    This should be called by a cron job or scheduler.
    """
    try:
        # Update all overdue fines
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

        # Get all approved borrow records that haven't been returned
        borrow_response = supabase.table("borrow").select("""
            id, user_id, book_id, return_date, return_date, status
        """).eq("status", "approved").is_("return_date", "null").execute()
        
        if not borrow_response.data:
            return {"success": True, "message": "No active borrows found."}

        updated_fines = []
        current_date = datetime.now().date().isoformat()
        
        for borrow in borrow_response.data:
            if borrow["return_date"]:
                # Calculate current fine amount
                fine_amount = calculate_fine_amount(borrow["return_date"], current_date)
                
                # Update or create fine record
                existing_fine = supabase.table("fines").select("*").eq("borrow_id", borrow["id"]).execute()
                
                if existing_fine.data:
                    # Update existing fine
                    fine_id = existing_fine.data[0]["id"]
                    if existing_fine.data[0]["amount"] != fine_amount:
                        supabase.table("fines").update({
                            "amount": fine_amount,
                            "reason": f"Overdue fine - {(datetime.strptime(current_date, '%Y-%m-%d').date() - datetime.strptime(borrow['return_date'], '%Y-%m-%d').date()).days} days late" if fine_amount > 0 else "No fine - returned on time"
                        }).eq("id", fine_id).execute()
                        updated_fines.append({"borrow_id": borrow["id"], "fine_amount": fine_amount})
                else:
                    # Create fine record if it doesn't exist
                    fine_data = {
                        "borrow_id": borrow["id"],
                        "user_id": borrow["user_id"],
                        "amount": fine_amount,
                        "paid": False,
                        "reason": f"Overdue fine - {(datetime.strptime(current_date, '%Y-%m-%d').date() - datetime.strptime(borrow['return_date'], '%Y-%m-%d').date()).days} days late" if fine_amount > 0 else "No fine",
                        "created_at": current_date
                    }
                    supabase.table("fines").insert(fine_data).execute()
                    updated_fines.append({"borrow_id": borrow["id"], "fine_amount": fine_amount})

        return {"success": True, "message": f"Daily fine update completed. Updated {len(updated_fines)} fines.", "updated_fines": updated_fines}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})