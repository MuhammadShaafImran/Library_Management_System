import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env.local')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment variables")
