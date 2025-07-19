from fastapi import APIRouter, HTTPException, Query, Request, status, Body
from core.supabase_client import get_supabase_client
from core.user import get_session_data
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from schemas.lending import BorrowerResponse
from models.user import UserType, UserStatus
from api.fine import update_overdue_fines
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/api/borrowers", response_model=List[BorrowerResponse])
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


        # Collect all librarian ids from borrow records
        librarian_ids = set()
        for borrow in borrow_records:
            if borrow.get("approved_by"):
                librarian_ids.add(borrow["approved_by"])

        # Fetch librarian names
        librarian_map = {}
        if librarian_ids:
            librarian_response = supabase.table("users").select("id, name").in_("id", list(librarian_ids)).execute()
            if librarian_response.data:
                librarian_map = {u["id"]: u["name"] for u in librarian_response.data}

        borrowers = []
        for borrow in borrow_records:
            user = users_map.get(borrow["user_id"])
            if not user:
                continue  # Skip if user not found or filtered out

            # Prepare extra fields for student/teacher
            department = None
            rollno = None
            batch = None
            semester = None
            designation = None
            if user["type"] == "student" and user["students"]:
                student_data = user["students"]
                department = student_data["department"]
                rollno = student_data["rollno"]
                batch = student_data["batch"]
                semester = student_data["semester"]
            elif user["type"] == "teacher" and user["teachers"]:
                teacher_data = user["teachers"]
                department = teacher_data["department"]
                designation = teacher_data["designation"]

            approved_by_id = borrow.get("approved_by")
            approved_by_name = librarian_map.get(approved_by_id) if approved_by_id else None

            borrower = BorrowerResponse(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                user_type=user["type"],
                phone=user["phone"],
                status=user["status"],
                last_login=user["last_login"],
                joining_date=user["joining_date"],
                books_borrowed=1,  # Each record is one borrow
                department=department,
                rollno=rollno,
                batch=batch,
                semester=semester,
                designation=designation,
                book_id=borrow.get("book_id"),
                request_description=borrow.get("request_description"),
                request_date=borrow.get("request_date"),
                return_date=borrow.get("return_date"),
                fine=borrow.get("fine"),
                approved_by=approved_by_name,
                approved_date=borrow.get("approved_date"),
                return_condition=borrow.get("return_condition"),
                borrow_status=borrow.get("status"),
                reminder_sent=borrow.get("reminder_sent")
            )
            borrowers.append(borrower)

        return borrowers

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/borrowers/{borrower_id}", response_model=BorrowerResponse)
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

@router.post("/api/borrow/request")
async def request_borrow(request: Request, data: Optional[dict] = None):
    supabase = get_supabase_client()
    if not supabase:
        return {"success":False, "error":"Supabase not connected"}
    
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
    
    # Update user's fines before allowing new borrow request
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_overdue_fines(user_id))
        loop.close()
        
        # Check if user has unpaid fines
        unpaid_fines = supabase.table("fines").select("amount").eq("user_id", user_id).eq("paid", False).execute()
        total_unpaid = sum(fine["amount"] for fine in unpaid_fines.data) if unpaid_fines.data else 0
        
        if total_unpaid > 0:
            return {"success": False, "error": f"You have unpaid fines totaling ${total_unpaid}. Please pay your fines before borrowing more books."}
            
    except Exception as fine_error:
        print(f"Error checking fines for borrow request: {fine_error}")
        # Continue with borrow request even if fine check fails
    
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

@router.post("/api/borrow/update_return_condition")
async def update_return_condition(request: Request, book_id: int = Body(...), return_condition: str = Body(...)):
    supabase = get_supabase_client()
    if not supabase:
        return JSONResponse(status_code=500, content={"success": False, "error": "Supabase client not found."})


    # Get session user (for security, only allow user or librarian to update)
    session = get_session_data(request)
    user_id = session.get('id')
    if not user_id:
        return JSONResponse(status_code=401, content={"success": False, "error": "Not logged in."})

    print("User: ", user_id,' book ID:', book_id, "return Condition: ", return_condition)
    # Find the borrow record for this book and user (pending/approved)
    borrow_resp = supabase.table("borrow").select("*").eq('user_id',user_id).eq("book_id", book_id).in_("status", ["pending", "approved"]).single().execute()
    borrow = borrow_resp.data
    if not borrow:
        return JSONResponse(status_code=404, content={"success": False, "error": "No active borrow record found for this book."})

    # Check if current date is less than return_date
    try:
        today = datetime.now().date()
        return_date = datetime.strptime(borrow["return_date"], "%Y-%m-%d").date()
    except Exception:
        return JSONResponse(status_code=400, content={"success": False, "error": "Invalid return date in record."})

    if today < return_date:
        # Early return, set status to rejected
        update = supabase.table("borrow").update({
            "return_condition": return_condition,
            "status": "returned"
        }).eq("id", borrow["id"]).execute()
        return {"success": True, "message": "Return condition updated and status set to returned"}
    else:
        # Check if fines for this borrow are paid
        fines_resp = supabase.table("fines").select("id, paid").eq("borrow_id", borrow["id"]).execute()
        fines = fines_resp.data
        if fines:
            unpaid = [f for f in fines if not f.get("paid")]
            if unpaid:
                return JSONResponse(status_code=400, content={"success": False, "error": "Fines for this borrow are not paid."})
        # Update return_condition and status to returned
        update = supabase.table("borrow").update({
            "return_condition": return_condition,
            "status": "returned"
        }).eq("id", borrow["id"]).execute()
        # Delete fine record(s) for this borrow if any
        if fines:
            fine_ids = [f["id"] for f in fines]
            supabase.table("fines").delete().in_("id", fine_ids).execute()
        return {"success": True, "message": "Return condition updated, status set to returned, and fines deleted if any."}

@router.get("/api/users/all")
async def get_all_users():
    supabase = get_supabase_client()
    if not supabase:
        return JSONResponse(status_code=500, content={"error": "Supabase client not found."})
        
    query = supabase.table("users").select("id, name, email").neq("type", "librarian")
    response = query.execute()
    
    if not response:
        return JSONResponse(status_code=500, content={"error": str(response.error)})
    
    return response.data 

@router.post("/api/borrow/admin_request")
async def admin_borrow_request(data: dict):
    supabase = get_supabase_client()
    if not supabase:
        return {"success": False, "error": "Supabase not connected"}
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    request_description = data.get('request_description', '').strip()
    return_date = data.get('return_date', '').strip()
    if not user_id or not book_id:
        return {"success": False, "error": "User ID and Book ID required."}
    if not request_description:
        return {"success": False, "error": "Request description is required."}
    if not return_date:
        return {"success": False, "error": "Return date is required."}
    try:
        _ = datetime.strptime(return_date, "%Y-%m-%d")
    except Exception:
        return {"success": False, "error": "Invalid return date format. Use YYYY-MM-DD."}
    # Check if already borrowed or pending
    existing = supabase.table("borrow").select("*").eq("user_id", user_id).eq("book_id", book_id).in_("status", ["pending", "approved"]).execute()
    if existing.data:
        return {"success": False, "error": "User already has a pending or approved request for this book."}
    # Insert borrow request
    result = supabase.table("borrow").insert({
        "user_id": user_id,
        "book_id": book_id,
        "request_description": request_description,
        "request_date": datetime.now().isoformat(),
        "return_date": return_date,
        "approved_by": None,
        "approved_date": None,
        "return_condition": None,
    }).execute()
    # Create notification for librarian(s)
    book = supabase.table("books").select("title,author").eq("id", book_id).single().execute().data
    user = supabase.table("users").select("name,email").eq("id", user_id).single().execute().data
    notif_msg = f"{user['name']} requested to borrow '{book['title']}' by {book['author']} (by admin)"
    supabase.table("notifications").insert({
        "user_id": user_id,
        "type": "borrow_request",
        "message": notif_msg,
        "book_id": book_id,
        "created_at": datetime.now().isoformat()
    }).execute()
    return {"success": True}

