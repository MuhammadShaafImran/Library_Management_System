from core.supabase_client import get_supabase_client

supabase = get_supabase_client()
# --- Helper Functions ---
def get_category_id(category_name: str) -> int:
    """
    Fetch the category_id from the categories table given a category name.
    Raises an Exception if not found.
    """
    if not category_name:
        raise Exception("Category name is required.")
    result = supabase.table("categories").select("id").eq("name", category_name).execute()
    if not result.data:
        raise Exception(f"Category '{category_name}' not found.")
    return result.data[0]['id']

def get_category_by_id(category_id: int):
    result = supabase.table("categories").select("*").eq("id", category_id).single().execute()
    if not result.data:
        return {}
    return result.data


def get_librarian_id(librarian_mail: str) -> int:
    """
    Fetch the librarian_id (added_by) for the book. This can be customized as needed.
    For now, returns the first librarian's id. Optionally, you can use session data.
    """
    result = supabase.table("users").select("id").eq("type", "librarian").eq("status", "active").eq('email',librarian_mail).limit(1).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]["id"]
    raise Exception("No active librarian found to assign as 'added_by'.")

# Get books by category name, excluding a specific book id (for related books)
async def get_books_by_category(category_name: str, exclude_id: int = 0, limit: int = 5):
    if not supabase:
        return []
    # Get category id from name
    cat_resp = supabase.table("categories").select("id").eq("name", category_name).single().execute()
    if not cat_resp.data:
        return []
    category_id = cat_resp.data["id"]
    query = supabase.table("books").select("id, title, author, cover_image").eq("category_id", category_id)
    if exclude_id != 0:
        query = query.neq("id", exclude_id)
    query = query.limit(limit)
    books_resp = query.execute()
    if not books_resp.data:
        return []
    # Return a list of dicts with id, title, author, cover_url
    return [
        {
            "id": b["id"],
            "title": b["title"],
            "author": b["author"],
            "cover_url": b.get("cover_image")
        }
        for b in books_resp.data
    ]