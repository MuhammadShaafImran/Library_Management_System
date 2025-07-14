from supabase import create_client, Client
from .config import SUPABASE_URL, SUPABASE_KEY

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase credentials are missing in config")
    return create_client(SUPABASE_URL, SUPABASE_KEY)
