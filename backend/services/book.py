from core.supabase_client import get_supabase_client
from datetime import datetime

supabase = get_supabase_client()

def validate_book_input(data: dict):
    required_fields = ['title', 'author', 'publisher', 'published_year', 'language', 'category_id', 'storage_type']
    for field in required_fields:
        if not data.get(field):
            return f"Missing required book field: {field}"
    if data['storage_type'] not in ["online", "offline"]:
        return "Invalid storage type."
    if data['storage_type'] == "online":
        for field in ['online_address', 'platform_name', 'access_url', 'format']:
            if not data.get(field):
                return f"Missing online book detail: {field}"
    if data['storage_type'] == "offline":
        for field in ['quantity', 'offline_address', 'shelf_no', 'room']:
            if not data.get(field):
                return f"Missing offline book detail: {field}"
    return None

def insert_book(data: dict):
    book_data = {
        "title": data["title"],
        "author": data["author"],
        "publisher": data["publisher"],
        "published_year": data["published_year"],
        "language": data["language"],
        "isbn": data.get("isbn"),
        "cover_image": data.get("cover_image"),
        "category_id": data["category_id"],
        "tags": data.get("tags"),
        "storage_type": data["storage_type"],
        "added_by": data.get("added_by")
    }
    result = supabase.table("books").insert(book_data).execute()
    if not result.data or not result.data[0].get("id"):
        raise Exception("Failed to insert book.")
    return result.data[0]["id"]

def insert_storage_data(book_id: int, data: dict):
    if data["storage_type"] == "online":
        online_data = {
            "id": book_id,
            "address": data["online_address"],
            "platform_name": data["platform_name"],
            "access_url": data["access_url"],
            "format": data["format"]
        }
        supabase.table("book_online").insert(online_data).execute()
    else:
        offline_data = {
            "id": book_id,
            "quantity": data["quantity"],
            "address": data["offline_address"],
            "shelf_no": data["shelf_no"],
            "room": data["room"]
        }
        supabase.table("book_offline").insert(offline_data).execute()

def update_book_and_storage(book_id: int, data: dict):
    book_data = {
        "title": data["title"],
        "author": data["author"],
        "publisher": data["publisher"],
        "published_year": data["published_year"],
        "language": data["language"],
        "isbn": data.get("isbn"),
        "cover_image": data.get("cover_image"),
        "tags": data.get("tags"),
        "storage_type": data["storage_type"],
        "added_by": 6
    }

    if data.get("category_id"):
        book_data["category_id"] = data["category_id"]

    supabase.table("books").update(book_data).eq("id", book_id).execute()

    if data["storage_type"] == "online":
        online_data = {
            "id": book_id,
            "address": data["online_address"],
            "platform_name": data["platform_name"],
            "access_url": data["access_url"],
            "format": data["format"]
        }
        supabase.table("book_online").upsert(online_data).execute()
    else:
        offline_data = {
            "id": book_id,
            "quantity": data["quantity"],
            "address": data["offline_address"],
            "shelf_no": data["shelf_no"],
            "room": data["room"]
        }
        supabase.table("book_offline").upsert(offline_data).execute()

async def get_book_by_id(book_id:int):
    if supabase:
        book_resp = supabase.table("books").select("*", "book_offline(*)", "book_online(*)").eq("id", book_id).single().execute()
        if book_resp.data:
            book = book_resp.data
            if book.get('book_offline'):
                book.update(book['book_offline'])
            if book.get('book_online'):
                book.update(book['book_online'])
            return book
    return None

def notification_count(id:int = 0, admin:bool =False) -> int:
    if supabase:
        if admin:
            print('Here')
            notifications = supabase.table("notifications").select("id").execute()
            print('notifications admin :', notifications.data)
            return len(notifications.data) if notifications.data else 0
        else:
            notifications = supabase.table("notifications").select("id").eq("user_id", id).execute()
            return len(notifications.data) if notifications.data else 0
    return 0