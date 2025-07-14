from core.user import clear_session
from fastapi import APIRouter, HTTPException, Query, Form, Request, Response
from core.supabase_client import get_supabase_client
from core.user import get_session_data, set_session_data
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional
from datetime import datetime


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post('/login')
def login_user(email: str = Form(...), password: str = Form(...)):
    supabase = get_supabase_client()
    if not supabase:
        return {"error": "Supabase client not found."}

    if not email or not password:
        return {"error": "Email and password are required"}, 400
    try:
        user_data = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()
        if not user_data.data:
            return {"error": "Invalid email or password"}, 401
        supabase.table('users').update({"last_login": datetime.now().isoformat()}).eq('email', email).execute()
        redirect_response = RedirectResponse(url="/", status_code=302)
        set_session_data(redirect_response, user_data.data[0])
        return redirect_response
    except Exception as e:
        return {"error": str(e)}, 400

@router.post("/register")
async def register(
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
        supabase = get_supabase_client()
        if not supabase:
            return JSONResponse(status_code=500, content={"error": "Supabase client not found."})

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
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        print("Error during registration:", str(e))
        return JSONResponse(status_code=400, content={"error": str(e)})

@router.post('/signout')
def signout(response: Response):
    clear_session(response)
    return RedirectResponse(url="/login", status_code=302)

@router.get("/user/profile", response_class=HTMLResponse)
async def get_user_profile(request: Request):
    session = get_session_data(request)
    supabase = get_supabase_client()
    if not supabase:
        return templates.TemplateResponse("error.html", {'request': request})
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

@router.get("/api/user/profile")
def get_user_profile_api(request: Request):
    session = get_session_data(request)
    supabase = get_supabase_client()
    if not supabase:
        return {"success": False, "error": "Supabase client not found."}

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
            "password":user.get('password'),
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
    
@router.post("/api/user/profile")
async def get_profile_by_name(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(None),
    rollno: str = Form(None),
    department : str = Form(None),
    batch: str = Form(None),
    semester: str = Form(None),
    designation: str = Form(None),
    admin: str = Form(None),
    status: str = Form(None),
    role: str = Form(...)
):
    session = get_session_data(request)
    user_email = session['email']
    supabase = get_supabase_client()
    if not supabase:
        return {"success": False, "error": "Supabase client not found."}
    try:
        # Get user by name
        user_data = supabase.table('users').select('*').eq('email', user_email).single().execute()
        user = user_data.data
        if not user:
            return {"success": False, "error": "User not found"}

        # Update users table
        update_user_fields = {
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "status": status,
        }
        # Remove None values
        update_user_fields = {k: v for k, v in update_user_fields.items() if v is not None}
        supabase.table('users').update(update_user_fields).eq('id', user['id']).execute()
        print('updated user:', update_user_fields)
        # Update type-specific table
        if role == 'student':
            update_student_fields = {}
            if rollno is not None:
                update_student_fields['rollno'] = rollno
            if department is not None:
                update_student_fields['department'] = department
            if batch is not None:
                update_student_fields['batch'] = batch
            if semester is not None:
                update_student_fields['semester'] = semester
            if update_student_fields:
                supabase.table('students').update(update_student_fields).eq('id', user['id']).execute()
        elif role == 'teacher':
            update_teacher_fields = {}
            if department is not None:
                update_teacher_fields['department'] = department
            if designation is not None:
                update_teacher_fields['designation'] = designation
            if update_teacher_fields:
                supabase.table('teachers').update(update_teacher_fields).eq('id', user['id']).execute()
        elif role == 'librarian':
            update_librarian_fields = {}
            if admin is not None:
                update_librarian_fields['admin'] = True if admin == 'true' else False
            if update_librarian_fields:
                supabase.table('librarians').update(update_librarian_fields).eq('id', user['id']).execute()

        # Fetch updated profile
        extra = {}
        if role == 'student':
            extra = supabase.table('students').select('*').eq('id', user['id']).single().execute().data
        elif role == 'teacher':
            extra = supabase.table('teachers').select('*').eq('id', user['id']).single().execute().data
        elif role == 'librarian':
            extra = supabase.table('librarians').select('*').eq('id', user['id']).single().execute().data
        profile = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "joined": user.get('joining_date'),
            "phone": update_user_fields.get('phone', user.get('phone')),
            "status": update_user_fields.get('status', user.get('status')),
            "last_login": user.get('last_login'),
        }
        if extra:
            for key, value in extra.items():
                profile[key] = value
                
        updated_user_data = supabase.table('users').select('*').eq('id', user['id']).single().execute().data
        response = JSONResponse({"success": True, "user": profile})
        set_session_data(response, updated_user_data)
        return response
    except Exception as e:
        return {"error": str(e)}