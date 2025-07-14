from fastapi import APIRouter, HTTPException, Query, Form, Request, Path
from core.supabase_client import get_supabase_client
from core.user import get_session_data
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
from datetime import datetime
from models.borrow import FineResponse

router = APIRouter()

@router.get("/api/notifications")
async def api_notifications(request: Request):
    session = get_session_data(request)
    user_id = session.get('id')
    user_type = session.get('type')

    supabase = get_supabase_client()
    if not supabase:
        return {"error": "Supabase client not found"}

    if user_type == 'librarian':
        notifs = supabase.table("notifications").select("*").eq("type", "borrow_request").order("created_at", desc=True).execute().data
    else:
        notifs = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data

    # Enrich notifications with user name and book title
    for n in notifs:
        # Add action/title for librarian
        if user_type == 'librarian' and n['type'] == 'borrow_request' and n.get('status') == 'rejected':
            n['action'] = 'Reject'
            n['title'] = 'Borrow Request'
        elif user_type == 'librarian' and n['type'] == 'borrow_request' and n.get('status') == 'approved':
            n['action'] = 'Approve'
            n['title'] = 'Borrow Request'
        elif user_type == 'librarian' and n['type'] == 'borrow_request' and n.get('status') == 'pending':
            n['action'] = 'Pending'
            n['title'] = 'Borrow Request'
        # else:
        #     n['action'] = ''
        #     n['title'] = 'Notification'

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

@router.post("/api/notifications/{notif_id}/approve")
async def approve_borrow_request(request: Request, notif_id: int = Path(...)):
    try:
        session = get_session_data(request)
        librarian_id = session.get('id')
        
        if not librarian_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Not authenticated."})
        
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"success": False, "error": "Supabase not connected"})
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

@router.post('/api/notifications/{notif_id}/reject')
async def reject_borrow_request(request: Request, notif_id: int = Path(...)):
    try:
        session = get_session_data(request)
        librarian_id = session.get('id')
        
        if not librarian_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Not authenticated."})
        
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"success": False, "error": "Supabase not connected"})
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
            "status": "rejected",
            "approved_by": librarian_id,
            "approved_date": datetime.now().isoformat()
        }).eq("id", borrow['id']).execute()
        
        # Update notification status
        supabase.table("notifications").update({"status": "rejected"}).eq("id", notif_id).execute()
        
        return JSONResponse(status_code=200, content={"success": True, "message": "Borrow request rejected successfully."})
        
    except Exception as e:
        print("Error in reject_borrow_request:", str(e))
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})