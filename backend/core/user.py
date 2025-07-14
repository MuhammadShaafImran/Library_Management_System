# FastAPI signout endpoint helper
from fastapi.responses import RedirectResponse
from .config import SECRET_KEY
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, Response
from services.book import notification_count

if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set and cannot be None.")

serializer = URLSafeTimedSerializer(SECRET_KEY)

# --- Session Helpers ---
def get_session_data(request: Request):
    cookie = request.cookies.get("session")
    if not cookie:
        return {}
    try:
        data = serializer.loads(cookie, max_age=3600)
        return data
    except Exception:
        return {}

def set_session_data(response: Response, data: dict):
    session_cookie = serializer.dumps(data)
    response.set_cookie(
        key="session",
        value=session_cookie,
        httponly=True,
        samesite="lax"
    )

def clear_session(response: Response):
    response.delete_cookie("session")


def get_user_name(request: Request) -> dict:
    session_data = get_session_data(request)
    name = session_data.get('name') if session_data else 'Unknown'
    role = session_data.get('type')
    ID = session_data.get('id') 
    if role == 'librarian':
        notif_count = notification_count(admin=True)
    else:
        notif_count = notification_count(id=int(ID) if ID is not None else 0)
    print('Notification count:', notif_count)
    
    return {
        "request": request,
        "name": name,
        "firstletter": name[0] if name else 'U',
        "notifications": notif_count
    }
    
